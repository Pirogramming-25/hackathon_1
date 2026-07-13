# guides/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet # GuideViewSet만 있으면 됩니다!

router = DefaultRouter()
router.register(r'guides', GuideViewSet) 

urlpatterns = [
    path('', include(router.urls)),
]