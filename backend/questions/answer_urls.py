from rest_framework.routers import DefaultRouter

from .views import AnswerViewSet

app_name = "answers"

router = DefaultRouter()
router.register("", AnswerViewSet, basename="answer")

urlpatterns = router.urls