import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Render 환경변수로 관리자 계정을 생성합니다."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "관리자 환경변수가 없어 관리자 생성을 건너뜁니다."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS("관리자 계정을 생성했습니다.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("기존 관리자 계정을 업데이트했습니다.")
            )