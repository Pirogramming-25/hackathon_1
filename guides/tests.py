# guides/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Guide, GuideImage, Visibility
from families.models import FamilyRelation
from questions.models import Question, Answer

User = get_user_model()

class GuidePromoteTests(APITestCase):
    def setUp(self):
        # 1. 테스트 유저 생성 (고유 이메일 적용)
        self.user = User.objects.create_user(username='questioner', email='q@test.com', password='password')
        self.other_user = User.objects.create_user(username='answerer', email='a@test.com', password='password')
        self.hacker = User.objects.create_user(username='hacker', email='h@test.com', password='password')
        
        # 2. 질문과 답변 생성
        self.question = Question.objects.create(author=self.user, title="질문", content="내용", category="FINANCE")
        self.answer = Answer.objects.create(question=self.question, author=self.other_user, content="답변")

    def tearDown(self):
        Guide.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        super().tearDown()

    def test_promote_by_questioner_success(self):
        """질문 작성자가 답변을 성공적으로 승격하는지 확인"""
        self.client.force_authenticate(user=self.user)
        url = f"/api/guides/answers/{self.answer.id}/promote/"
        
        response = self.client.post(url, {"title": "설명서", "category": "FINANCE", "visibility": "PUBLIC"})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Guide.objects.filter(source_answer=self.answer).count(), 1)

    def test_promote_forbidden_by_non_questioner(self):
        """질문 작성자가 아닌 사람이 승격 시도시 403 확인"""
        self.client.force_authenticate(user=self.hacker)
        url = f"/api/guides/answers/{self.answer.id}/promote/"
        
        response = self.client.post(url, {"title": "실패", "category": "FINANCE"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_promote_duplicate_prevention(self):
        """같은 질문에 이미 설명서가 있으면 중복 승격 불가(409) 확인"""
        self.client.force_authenticate(user=self.user)
        # 이미 승격됨
        Guide.objects.create(author=self.user, title="기존", category="FINANCE", source_answer=self.answer)
        
        # 두 번째 답변 생성 및 승격 시도
        new_answer = Answer.objects.create(question=self.question, author=self.other_user, content="두번째")
        url = f"/api/guides/answers/{new_answer.id}/promote/"
        
        response = self.client.post(url, {"title": "중복", "category": "FINANCE"})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_promote_invalid_data_400(self):
        """필수 필드 누락 시 400 확인"""
        self.client.force_authenticate(user=self.user)
        url = f"/api/guides/answers/{self.answer.id}/promote/"
        
        # title 누락
        response = self.client.post(url, {"category": "FINANCE"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])


class PrivateGuideFamilyAccessTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="guide-author",
            email="guide-author@test.com",
            password="password",
        )
        self.family = User.objects.create_user(
            username="family-user",
            email="family-user@test.com",
            password="password",
        )
        self.stranger = User.objects.create_user(
            username="stranger-user",
            email="stranger-user@test.com",
            password="password",
        )
        user1, user2 = sorted([self.author, self.family], key=lambda user: user.pk)
        FamilyRelation.objects.create(
            user1=user1,
            user2=user2,
            requester=self.author,
            status=FamilyRelation.Status.ACCEPTED,
        )
        self.private_guide = Guide.objects.create(
            author=self.author,
            title="가족용 설명서",
            category="LIFE",
            visibility=Visibility.PRIVATE,
        )

    def test_accepted_family_can_retrieve_private_guide(self):
        self.client.force_authenticate(user=self.family)

        response = self.client.get(f"/api/guides/{self.private_guide.pk}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accepted_family_sees_private_guide_in_list(self):
        self.client.force_authenticate(user=self.family)

        response = self.client.get("/api/guides/")
        guide_ids = [guide["id"] for guide in response.data["data"]["results"]]

        self.assertIn(self.private_guide.pk, guide_ids)

    def test_non_family_cannot_retrieve_private_guide(self):
        self.client.force_authenticate(user=self.stranger)

        response = self.client.get(f"/api/guides/{self.private_guide.pk}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_retrieve_private_guide(self):
        response = self.client.get(f"/api/guides/{self.private_guide.pk}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GuideListSearchTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="search-author",
            email="search-author@test.com",
            password="password",
        )

    def test_search_includes_step_description(self):
        guide = Guide.objects.create(
            author=self.author,
            title="휴대전화 사용법",
            category="LIFE",
            visibility=Visibility.PUBLIC,
        )
        GuideImage.objects.create(
            guide=guide,
            image="guides/test-image.jpg",
            description="카카오톡 인증서를 발급합니다.",
            display_order=1,
        )

        response = self.client.get("/api/guides/", {"search": "인증서"})
        guide_ids = [item["id"] for item in response.data["data"]["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(guide.pk, guide_ids)

    def test_search_includes_korean_category_name(self):
        guide = Guide.objects.create(
            author=self.author,
            title="은행 앱 사용법",
            category="FINANCE",
            visibility=Visibility.PUBLIC,
        )

        response = self.client.get("/api/guides/", {"search": "금융"})
        guide_ids = [item["id"] for item in response.data["data"]["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(guide.pk, guide_ids)

    def test_search_includes_category_code(self):
        guide = Guide.objects.create(
            author=self.author,
            title="병원 앱 사용법",
            category="MEDICAL",
            visibility=Visibility.PUBLIC,
        )

        response = self.client.get("/api/guides/", {"search": "medical"})
        guide_ids = [item["id"] for item in response.data["data"]["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(guide.pk, guide_ids)

    def test_list_response_contains_page_size(self):
        for index in range(11):
            Guide.objects.create(
                author=self.author,
                title=f"설명서 {index}",
                category="LIFE",
                visibility=Visibility.PUBLIC,
            )

        response = self.client.get("/api/guides/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["page_size"], 10)
        self.assertEqual(response.data["data"]["count"], 11)
