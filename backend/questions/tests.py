
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Answer, AnswerImage, Question, QuestionImage

User = get_user_model()


def make_image(name="test.png"):
    """테스트용 최소 크기 PNG 이미지 파일을 즉석에서 생성한다."""
    buf = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buf, "PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


# =========================================================
# 모델 테스트
# =========================================================

class QuestionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author", email="author@test.com", password="pass1234"
        )

    def test_default_status_is_waiting(self):
        question = Question.objects.create(
            author=self.user, title="t", content="c", category="LIFE"
        )
        self.assertEqual(question.status, Question.Status.WAITING)

    def test_delete_question_cascades_question_image(self):
        question = Question.objects.create(
            author=self.user, title="t", content="c", category="LIFE"
        )
        QuestionImage.objects.create(
            question=question, image=make_image(), display_order=1
        )
        question.delete()
        self.assertEqual(QuestionImage.objects.count(), 0)

    def test_delete_question_cascades_answer(self):
        question = Question.objects.create(
            author=self.user, title="t", content="c", category="LIFE"
        )
        Answer.objects.create(question=question, author=self.user, content="a")
        question.delete()
        self.assertEqual(Answer.objects.count(), 0)

    def test_delete_answer_cascades_answer_image(self):
        question = Question.objects.create(
            author=self.user, title="t", content="c", category="LIFE"
        )
        answer = Answer.objects.create(question=question, author=self.user, content="a")
        AnswerImage.objects.create(answer=answer, image=make_image(), display_order=1)
        answer.delete()
        self.assertEqual(AnswerImage.objects.count(), 0)

    def test_duplicate_display_order_blocked(self):
        question = Question.objects.create(
            author=self.user, title="t", content="c", category="LIFE"
        )
        QuestionImage.objects.create(
            question=question, image=make_image("a.png"), display_order=1
        )
        with self.assertRaises(IntegrityError):
            QuestionImage.objects.create(
                question=question, image=make_image("b.png"), display_order=1
            )


# =========================================================
# 질문 API 테스트
# =========================================================

class QuestionAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", email="author@test.com", password="pass1234"
        )
        self.other = User.objects.create_user(
            username="other", email="other@test.com", password="pass1234"
        )
        self.question = Question.objects.create(
            author=self.author, title="원래 제목", content="c", category="LIFE"
        )

    def test_list_requires_authentication(self):
        response = self.client.get("/api/questions/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_success(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.get("/api/questions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["count"], 1)

    def test_create_question_success(self):
        self.client.force_authenticate(user=self.author)
        payload = {"title": "새 질문", "content": "내용", "category": "MEDICAL"}
        response = self.client.post("/api/questions/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "새 질문")

    def test_create_question_with_6_images_fails(self):
        self.client.force_authenticate(user=self.author)
        payload = {
            "title": "새 질문",
            "content": "내용",
            "category": "MEDICAL",
            "images": [make_image(f"{i}.png") for i in range(6)],
        }
        response = self.client.post("/api/questions/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_other_user_cannot_update(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f"/api/questions/{self.question.id}/", {"title": "변경 시도"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_delete(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f"/api/questions/{self.question.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_and_delete(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(
            f"/api/questions/{self.question.id}/", {"title": "수정된 제목"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], "수정된 제목")

        response = self.client.delete(f"/api/questions/{self.question.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())

    def test_status_change_success(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(
            f"/api/questions/{self.question.id}/status/", {"status": "RESOLVED"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "RESOLVED")

    def test_invalid_status_value_fails(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(
            f"/api/questions/{self.question.id}/status/", {"status": "HELLO"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================
# 답변 API 테스트
# =========================================================

class AnswerAPITests(APITestCase):
    def setUp(self):
        self.question_author = User.objects.create_user(
            username="q_author", email="q_author@test.com", password="pass1234"
        )
        self.answer_author = User.objects.create_user(
            username="a_author", email="a_author@test.com", password="pass1234"
        )
        self.other = User.objects.create_user(
            username="other", email="other2@test.com", password="pass1234"
        )
        self.question = Question.objects.create(
            author=self.question_author, title="t", content="c", category="LIFE"
        )
        self.answer = Answer.objects.create(
            question=self.question, author=self.answer_author, content="기존 답변"
        )

    def test_create_answer_success(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", {"content": "새 답변"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_create_answer_with_5_images_fails(self):
        self.client.force_authenticate(user=self.other)
        payload = {
            "content": "새 답변",
            "images": [make_image(f"{i}.png") for i in range(5)],
        }
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", payload, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_resolved_question_blocks_answer(self):
        self.question.status = Question.Status.RESOLVED
        self.question.save()
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", {"content": "새 답변"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_waiting_again_allows_answer(self):
        self.question.status = Question.Status.RESOLVED
        self.question.save()
        self.question.status = Question.Status.WAITING
        self.question.save()

        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", {"content": "새 답변"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_other_user_cannot_update_answer(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f"/api/answers/{self.answer.id}/", {"content": "변경 시도"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_delete_answer(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f"/api/answers/{self.answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_author_can_update_and_delete(self):
        self.client.force_authenticate(user=self.answer_author)
        response = self.client.patch(
            f"/api/answers/{self.answer.id}/", {"content": "수정된 답변"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["content"], "수정된 답변")

        response = self.client.delete(f"/api/answers/{self.answer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())

    def test_answer_with_image_descriptions_saved_correctly(self):
        self.client.force_authenticate(user=self.other)
        payload = {
            "content": "새 답변",
            "images": [make_image("a.png"), make_image("b.png")],
            "image_descriptions": ["1단계 설명", "2단계 설명"],
        }
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", payload, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        images = response.data["data"]["images"]
        self.assertEqual(images[0]["description"], "1단계 설명")
        self.assertEqual(images[1]["description"], "2단계 설명")

    def test_answer_with_mismatched_image_description_count_fails(self):
        self.client.force_authenticate(user=self.other)
        payload = {
            "content": "새 답변",
            "images": [make_image("a.png"), make_image("b.png")],
            "image_descriptions": ["설명 1개만"],
        }
        response = self.client.post(
            f"/api/questions/{self.question.id}/answers/", payload, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================
# Guide Data 테스트
# =========================================================

class GuideDataAPITests(APITestCase):
    def setUp(self):
        self.answer_author = User.objects.create_user(
            username="a_author", email="a_author2@test.com", password="pass1234"
        )
        self.other = User.objects.create_user(
            username="other", email="other3@test.com", password="pass1234"
        )
        self.question = Question.objects.create(
            author=self.answer_author, title="t", content="c", category="MEDICAL"
        )
        self.answer = Answer.objects.create(
            question=self.question, author=self.answer_author, content="답변 내용"
        )
        AnswerImage.objects.create(
            answer=self.answer, image=make_image("second.png"), display_order=2
        )
        AnswerImage.objects.create(
            answer=self.answer, image=make_image("first.png"), display_order=1
        )

    def test_author_can_fetch_guide_data(self):
        self.client.force_authenticate(user=self.answer_author)
        response = self.client.get(f"/api/answers/{self.answer.id}/guide-data/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_other_user_cannot_fetch_guide_data(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f"/api/answers/{self.answer.id}/guide-data/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_matches_question_category(self):
        self.client.force_authenticate(user=self.answer_author)
        response = self.client.get(f"/api/answers/{self.answer.id}/guide-data/")
        self.assertEqual(response.data["data"]["category"], "MEDICAL")

    def test_images_ordered_by_display_order(self):
        self.client.force_authenticate(user=self.answer_author)
        response = self.client.get(f"/api/answers/{self.answer.id}/guide-data/")
        orders = [img["display_order"] for img in response.data["data"]["images"]]
        self.assertEqual(orders, [1, 2])

class MyPageAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="me", email="me@test.com", password="pass1234"
        )
        self.other = User.objects.create_user(
            username="other4", email="other4@test.com", password="pass1234"
        )
        self.my_question = Question.objects.create(
            author=self.user, title="내 질문", content="c", category="LIFE"
        )
        self.other_question = Question.objects.create(
            author=self.other, title="남 질문", content="c", category="LIFE"
        )
        self.my_answer = Answer.objects.create(
            question=self.other_question, author=self.user, content="내 답변"
        )
        Answer.objects.create(
            question=self.my_question, author=self.other, content="남 답변"
        )

    def test_my_question_list_only_shows_own_questions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/me/questions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [q["title"] for q in response.data["data"]["results"]]
        self.assertEqual(titles, ["내 질문"])

    def test_my_answer_list_only_shows_own_answers(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/me/answers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contents = [a["content"] for a in response.data["data"]["results"]]
        self.assertEqual(contents, ["내 답변"])