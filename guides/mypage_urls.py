# guides/mypage_urls.py
from django.urls import path
from .mypage_views import MyGuideListView, MyScrapListView 

urlpatterns = [
    path('guides/', MyGuideListView.as_view(), name='my-guides'),
    path('scraps/', MyScrapListView.as_view(), name='my-scraps'),
]