from django.urls import path

from .views import MyAnswerListView

app_name = "mypage_answers"

urlpatterns = [
    path("", MyAnswerListView.as_view(), name="my-answers"),
]