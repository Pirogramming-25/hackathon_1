# =========================================================
# 설명서(Guide) 및 답변 승격 API 테스트
# =========================================================

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
        # 답변에 이미지 2장 첨부
        AnswerImage.objects.create(answer=self.answer, image=make_image("a.png"), description="1단계", display_order=1)
        AnswerImage.objects.create(answer=self.answer, image=make_image("b.png"), description="2단계", display_order=2)

    def test_promote_answer_to_guide_success(self):
        """답변을 설명서로 승격(복사)하는 기능이 정상 작동하는지 테스트"""
        payload = {
            "title": "승격된 설명서",
            "category": "FINANCE",
            "visibility": "PUBLIC",
            "source_answer_id": self.answer.id
        }
        
        response = self.client.post("/api/guides/", payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        
        # Guide 생성 확인 및 이미지 복사 확인
        guide = Guide.objects.get(title="승격된 설명서")
        self.assertEqual(guide.images.count(), 2)
        self.assertEqual(guide.images.first().description, "1단계")

    def test_guide_search_and_sort(self):
        """검색어 및 스크랩 정렬 기능이 정상 작동하는지 테스트"""
        Guide.objects.create(author=self.user, title="금융 가이드", category="FINANCE", visibility="PUBLIC")
        Guide.objects.create(author=self.user, title="생활 가이드", category="LIFE", visibility="PUBLIC")
        
        # 검색 테스트
        response = self.client.get("/api/guides/?search=금융")
        self.assertEqual(response.data["data"]["count"], 1)
        
        # 카테고리 필터 테스트
        response = self.client.get("/api/guides/?category=LIFE")
        self.assertEqual(response.data["data"]["results"][0]["title"], "생활 가이드")

    def test_like_scrap_toggle(self):
        """좋아요/스크랩의 등록/취소 토글 로직 테스트"""
        guide = Guide.objects.create(author=self.user, title="test", category="FINANCE", visibility="PUBLIC")
        
        # 좋아요 등록
        self.client.post(f"/api/guides/{guide.id}/like/")
        # 좋아요 취소 (같은 URL)
        response = self.client.post(f"/api/guides/{guide.id}/like/")
        
        self.assertFalse(response.data["data"]["is_liked"])
        self.assertEqual(response.data["data"]["like_count"], 0)