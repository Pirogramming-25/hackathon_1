# guides/tests.py
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from io import BytesIO
from PIL import Image

from .models import Guide, Category, Visibility, GuideImage
from questions.models import Question, Answer, AnswerImage

User = get_user_model()

def make_image(name="test.png"):
    buf = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buf, "PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")

class GuideAPITests(APITestCase):
    def setUp(self):
        # 유저 생성 시 고유한 이메일 명시 (에러 방지)
        self.user = User.objects.create_user(username='tester', email='tester@test.com', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.question = Question.objects.create(
            author=self.user, title="카카오톡 송금", content="?", category="FINANCE"
        )
        self.answer = Answer.objects.create(
            question=self.question, author=self.user, content="송금 방법입니다"
        )
        AnswerImage.objects.create(answer=self.answer, image=make_image("a.png"), description="1단계", display_order=1)
        AnswerImage.objects.create(answer=self.answer, image=make_image("b.png"), description="2단계", display_order=2)

    def tearDown(self):
        Guide.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        super().tearDown()

    def test_promote_answer_success(self):
        """채택된 답변 승격 기능 테스트"""
        # 1. 답변을 채택 상태로 설정
        self.answer.is_accepted = True
        self.answer.save()

        url = f"/api/guides/answers/{self.answer.id}/promote/"
        payload = {
            "title": "승격된 설명서",
            "category": "FINANCE",
            "visibility": "PUBLIC"
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_createED)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(Guide.objects.filter(title="승격된 설명서").count(), 1)

    def test_promote_answer_not_accepted(self):
        """채택되지 않은 본인 답변 승격 시 400 에러 및 객체 미생성 확인"""
        # setUp에서 생성된 self.answer는 is_accepted=False 상태임
        url = f"/api/guides/answers/{self.answer.id}/promote/"
        payload = {
            "title": "미채택 설명서",
            "category": "FINANCE",
            "visibility": "PUBLIC"
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("message"), "채택된 답변만 설명서로 등록할 수 있습니다.")
        self.assertEqual(Guide.objects.filter(title="미채택 설명서").count(), 0)

    def test_promote_answer_forbidden(self):
        """다른 사용자의 답변(채택됨) 승격 시 403 에러 확인"""
        # 다른 유저 생성 시 고유한 이메일 명시 (에러 방지)
        other_user = User.objects.create_user(
            username='other', 
            email='other@test.com', 
            password='password'
        )
        other_answer = Answer.objects.create(
            question=self.question, author=other_user, content="타인의 답변"
        )
        other_answer.is_accepted = True
        other_answer.save()

        url = f"/api/guides/answers/{other_answer.id}/promote/"
        payload = {"title": "공격", "category": "FINANCE", "visibility": "PUBLIC"}
        
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Guide.objects.filter(title="공격").count(), 0)

    def test_guidee_search_and_filter(self):
        Guide.objects.all().delete() 
        Guide.objects.create(author=self.user, title="금융 가이드", category="FINANCE", visibility="PUBLIC")
        Guide.objects.create(author=self.user, title="생활 가이드", category="LIFE", visibility="PUBLIC")
        
        # 검색 테스트
        response = self.client.get("/api/guides/?search=금융")
        results = response.data["data"]["results"] 
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "금융 가이드")
        
        # 카테고리 필터 테스트
        response = self.client.get("/api/guides/?category=LIFE")
        results = response.data["data"]["results"]
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "생활 가이드")

    def test_like_scrap_toggle(self):
        """좋아요/스크랩 토글 로직 테스트"""
        guide = Guide.objects.create(author=self.user, title="토글 테스트", category="FINANCE", visibility="PUBLIC")
        
        self.client.post(f"/api/guides/{guide.id}/like/")
        response = self.client.post(f"/api/guides/{guide.id}/like/")
        
        self.assertFalse(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["like_count"], 0)