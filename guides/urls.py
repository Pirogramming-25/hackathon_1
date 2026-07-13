# guides/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import GuideViewSet

router = SimpleRouter()
router.register('', GuideViewSet, basename='guide')

urlpatterns = [
    path('', include(router.urls)),
]