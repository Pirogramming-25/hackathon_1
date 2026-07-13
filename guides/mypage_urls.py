# guides/mypage_urls.py
from django.urls import path
# 변경됨: .views 대신 .mypage_views에서 가져옵니다.
from .mypage_views import MyGuideListView, MyScrapListView 

urlpatterns = [
    path('guides/', MyGuideListView.as_view(), name='my-guides'),
    path('scraps/', MyScrapListView.as_view(), name='my-scraps'),
]