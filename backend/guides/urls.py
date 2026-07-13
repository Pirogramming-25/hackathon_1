from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet

app_name = "guides"

router = DefaultRouter()

router.register(r'guides', GuideViewSet)

urlpatterns = [
    path('', include(router.urls)),
]