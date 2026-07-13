from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UIMode(models.TextChoices):
        BASIC = "BASIC", "기본 모드"
        EASY = "EASY", "쉬운 모드"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    ui_mode = models.CharField(
        max_length=10,
        choices=UIMode.choices,
        default=UIMode.BASIC,
    )

    def __str__(self) -> str:
        return self.username
