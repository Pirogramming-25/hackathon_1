from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "추가 정보",
            {
                "fields": (
                    "name",
                    "birth_date",
                    "ui_mode",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "추가 정보",
            {
                "fields": (
                    "email",
                    "name",
                    "birth_date",
                    "ui_mode",
                )
            },
        ),
    )

    list_display = (
        "id",
        "username",
        "email",
        "name",
        "ui_mode",
        "is_staff",
    )