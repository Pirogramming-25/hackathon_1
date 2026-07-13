from django.urls import path

from .views import MyQuestionListView

app_name = "mypage_questions"

urlpatterns = [
    path("", MyQuestionListView.as_view(), name="my-questions"),
]