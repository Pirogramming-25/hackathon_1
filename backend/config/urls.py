from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse(
        {
            "success": True,
            "message": "Server is running.",
        }
    )


def index(request):
    return JsonResponse(
        {
            "success": True,
            "message": "Hackathon backend server is running.",
            "endpoints": {
                "admin": "/admin/",
                "health": "/api/health/",
                "auth": "/api/auth/",
                "users": "/api/users/",
                "guides": "/api/guides/",
                "questions": "/api/questions/",
                "families": "/api/families/",
            },
        }
    )


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api/health/", health_check),

    path("api/auth/", include("accounts.urls")),
    path("api/users/", include("accounts.user_urls")),
    path("api/guides/", include("guides.urls")),
    path("api/questions/", include("questions.question_urls")),
    path("api/answers/", include("questions.answer_urls")),
    path("api/users/me/", include("guides.mypage_urls")),
    path("api/users/me/questions/", include("questions.mypage_question_urls")),  # 추가
    path("api/users/me/answers/", include("questions.mypage_answer_urls")),      # 추가
    path("api/families/", include("families.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
