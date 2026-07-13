from rest_framework import viewsets
from rest_framework.decorators import action
from .permissions import IsAuthorOrReadOnly
from rest_framework.response import Response
from .models import Guide
from .serializers import GuideSerializer

class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer

    permission_classes = [IsAuthorOrReadOnly]

    # 1. 좋아요 등록/취소 (POST/DELETE /api/guides/{id}/like/)
    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        guide = self.get_object()
        # 여기에 좋아요 로직 작성 (Like 모델 생성/삭제)
        return Response({'status': 'liked/unliked'})

    # 2. 스크랩 등록/취소 (POST/DELETE /api/guides/{id}/scrap/)
    @action(detail=True, methods=['post', 'delete'])
    def scrap(self, request, pk=None):
        guide = self.get_object()
        # 여기에 스크랩 로직 작성 (Scrap 모델 생성/삭제)
        return Response({'status': 'scrapped/unscrapped'})
    
    def perform_create(self, serializer):
        # 이렇게 하면 입력 폼에 author를 넣지 않아도 
        # 로그인한 유저가 자동으로 작성자로 등록됩니다.
        serializer.save(author=self.request.user)