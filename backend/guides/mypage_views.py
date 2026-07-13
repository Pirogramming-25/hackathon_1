from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count, Exists, OuterRef

from .models import Guide, GuideLike, GuideScrap
from .serializers import GuideSerializer

class MyGuideListView(generics.ListAPIView):
    serializer_class = GuideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Guide.objects.select_related('author').prefetch_related('images')
        
        queryset = queryset.filter(author=user)
        
        queryset = queryset.annotate(
            is_liked=Exists(GuideLike.objects.filter(user=user, guide=OuterRef('pk'))),
            is_scrapped=Exists(GuideScrap.objects.filter(user=user, guide=OuterRef('pk'))),
            like_count=Count('likes', distinct=True),
            scrap_count=Count('scraps', distinct=True)
        ).order_by("-created_at")
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": response.data if response.data else [],
            "message": "내가 만든 설명서 목록 조회에 성공했습니다."
        })
    
class MyScrapListView(generics.ListAPIView):
    serializer_class = GuideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Guide.objects.select_related('author').prefetch_related('images')
        
        queryset = queryset.filter(scraps__user=user)
        
        queryset = queryset.annotate(
            is_liked=Exists(GuideLike.objects.filter(user=user, guide=OuterRef('pk'))),
            is_scrapped=Exists(GuideScrap.objects.filter(user=user, guide=OuterRef('pk'))),
            like_count=Count('likes', distinct=True),
            scrap_count=Count('scraps', distinct=True)
        ).order_by("-scraps__created_at")
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": response.data if response.data else [],
            "message": "저장한 설명서 목록 조회에 성공했습니다."
        })