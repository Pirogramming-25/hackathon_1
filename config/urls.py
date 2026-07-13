from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView


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
            "message": "Hackathon Django server is running.",
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

    path(
        "questions/",
        TemplateView.as_view(
            template_name="question_list.html",
            extra_context={"active_nav": "question_list"},
        ),
        name="question_page_list",
    ),
    path(
        "questions/create/",
        TemplateView.as_view(template_name="question_create.html"),
        name="question_create",
    ),
    path(
        "questions/<int:pk>/",
        TemplateView.as_view(template_name="question_detail.html"),
        name="question_detail",
    ),

    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),
    path("signup/", TemplateView.as_view(template_name="signup.html"), name="signup"),
    path("my-page/", TemplateView.as_view(template_name="my_page.html"), name="my_page"),
    path("my-info/", TemplateView.as_view(template_name="myinfo.html"), name="my_info"),
    path(
        "family-connect/",
        TemplateView.as_view(template_name="family_connect.html"),
        name="family_connect",
    ),

    
    path("api/", index),
    path("admin/", admin.site.urls),
    path("api/health/", health_check),

    path("api/auth/", include("accounts.urls")),
    path("api/guides/", include("guides.urls")),
    path("api/questions/", include("questions.question_urls")),
    path("api/answers/", include("questions.answer_urls")),
    path("api/users/me/", include("guides.mypage_urls")),
    path("api/users/me/questions/", include("questions.mypage_question_urls")),
    path("api/users/me/answers/", include("questions.mypage_answer_urls")),
    path("api/users/", include("accounts.user_urls")),
    path("api/families/", include("families.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
