from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet

app_name = "questions"

router = DefaultRouter()
router.register("", QuestionViewSet, basename="question")

urlpatterns = router.urls