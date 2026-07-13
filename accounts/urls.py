from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "check-username/",
        views.CheckUsernameView.as_view(),
        name="check-username",
    ),
    path("check-email/", views.CheckEmailView.as_view(), name="check-email"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
