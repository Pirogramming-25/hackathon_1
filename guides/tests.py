from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from io import BytesIO
from PIL import Image

# 가이드 관련 모델 및 기타 필요한 것들
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
        self.user = User.objects.create_user(username='tester', password='password')
        self.client.force_authenticate(user=self.user)
        
        # 질문과 답변 준비
        self.question = Question.objects.create(
            author=self.user, title="카카오톡 송금", content="?", category="FINANCE"
        )
        self.answer = Answer.objects.create(
            question=self.question, author=self.user, content="송금 방법입니다"
        )
        AnswerImage.objects.create(answer=self.answer, image=make_image("a.png"), description="1단계", display_order=1)
        AnswerImage.objects.create(answer=self.answer, image=make_image("b.png"), description="2단계", display_order=2)

    def tearDown(self):
        """테스트마다 데이터베이스를 깨끗하게 비웁니다."""
        Guide.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        super().tearDown()

    def test_promote_answer_success(self):
        """답변 승격 기능 테스트"""
        url = f"/api/guides/answers/{self.answer.id}/promote/"
        payload = {
            "title": "승격된 설명서",
            "category": "FINANCE",
            "visibility": "PUBLIC"
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        
        # 데이터베이스에 가이드가 생성되었는지 확인
        self.assertEqual(Guide.objects.filter(title="승격된 설명서").count(), 1)

    def test_guide_search_and_filter(self):
        """검색 및 카테고리 필터 테스트"""
        Guide.objects.all().delete()
        Guide.objects.create(author=self.user, title="금융 가이드", category="FINANCE", visibility="PUBLIC")
        Guide.objects.create(author=self.user, title="생활 가이드", category="LIFE", visibility="PUBLIC")
        
        # 검색 테스트
        response = self.client.get("/api/guides/?search=금융")
        
        # [수정] response.data["data"]["results"] 를 사용하여 리스트 길이를 확인
        results = response.data["data"]["results"]
        
        self.assertEqual(len(results), 1, f"검색 결과가 1개여야 하는데 {len(results)}개가 나왔습니다.")
        self.assertEqual(results[0]["title"], "금융 가이드")
        
        # 카테고리 필터 테스트
        response = self.client.get("/api/guides/?category=LIFE")
        results = response.data["data"]["results"]
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "생활 가이드")

    def test_like_scrap_toggle(self):
        """좋아요/스크랩의 등록/취소 토글 로직 테스트"""
        guide = Guide.objects.create(author=self.user, title="토글 테스트", category="FINANCE", visibility="PUBLIC")
        
        # 좋아요 등록/취소
        self.client.post(f"/api/guides/{guide.id}/like/")
        response = self.client.post(f"/api/guides/{guide.id}/like/")
        
        self.assertFalse(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["like_count"], 0)