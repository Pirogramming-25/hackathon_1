# backend/questions/models.py

from django.conf import settings
from django.db import models


class Category(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", "정부"
    FINANCE = "FINANCE", "금융"
    MEDICAL = "MEDICAL", "의료"
    LIFE = "LIFE", "생활"
    ETC = "ETC", "기타"


class Question(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING", "답변 대기"
        RESOLVED = "RESOLVED", "해결 완료"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="questions/")
    description = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "display_order"],
                name="unique_question_image_order",
            )
        ]
        ordering = ["display_order"]

    def __str__(self):
        return f"QuestionImage({self.question_id}, {self.display_order})"


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer({self.id}) - Question({self.question_id})"


class AnswerImage(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="answers/")
    description = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "display_order"],
                name="unique_answer_image_order",
            )
        ]
        ordering = ["display_order"]

    def __str__(self):
        return f"AnswerImage({self.answer_id}, {self.display_order})"