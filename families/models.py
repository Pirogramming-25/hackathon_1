from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class FamilyRelation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "대기"
        ACCEPTED = "ACCEPTED", "수락"
        REJECTED = "REJECTED", "거절"

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_relations_as_user1",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_relations_as_user2",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_family_requests",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_family_relation_pair",
            ),
            models.CheckConstraint(
                check=models.Q(user1_id__lt=models.F("user2_id")),
                name="family_relation_user1_lt_user2",
            ),
        ]
        ordering = ["-updated_at"]

    def clean(self):
        if self.user1_id and self.user2_id and self.user1_id >= self.user2_id:
            raise ValidationError("user1에는 더 작은 사용자 PK를 저장해야 합니다.")
        if self.requester_id not in {self.user1_id, self.user2_id}:
            raise ValidationError("요청자는 가족 관계의 당사자여야 합니다.")

    def other_user(self, user):
        if user.pk == self.user1_id:
            return self.user2
        if user.pk == self.user2_id:
            return self.user1
        return None

    def is_participant(self, user):
        return user.pk in {self.user1_id, self.user2_id}

    def receiver(self):
        if self.requester_id == self.user1_id:
            return self.user2
        return self.user1

    def __str__(self):
        return f"{self.user1_id}-{self.user2_id} ({self.status})"
