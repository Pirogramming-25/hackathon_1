# guides/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.db.models import Q, Count, Exists, OuterRef

from .models import Guide, Visibility, GuideLike, GuideScrap
from .serializers import GuideSerializer, GuidePromoteSerializer
from .permissions import IsAuthorOrReadOnly
from questions.models import Answer 

class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = [IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    
    # 페이지네이션 제거 코드를 삭제했습니다. (settings.py의 기본 설정이 적용됨)

    # 답변 승격 엔드포인트: /api/guides/answers/<answer_id>/promote/
    @action(detail=False, methods=['post'], url_path=r'answers/(?P<answer_id>\d+)/promote')
    def promote_answer(self, request, answer_id=None):
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response({"error": "존재하지 않는 답변입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 1. 작성자 본인 확인
        if answer.author != request.user:
            return Response({"error": "본인이 작성한 답변만 등록할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 2. 채택된 답변인지 확인
        if not answer.is_accepted:
            return Response({
                "success": False,
                "data": None,
                "message": "채택된 답변만 설명서로 등록할 수 있습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. 승격 처리
        serializer = GuidePromoteSerializer(
            data=request.data, 
            context={'request': request, 'answer': answer}
        )
        
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response({"success": True, "message": "성공적으로 승격되었습니다."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Guide.objects.select_related('author').prefetch_related('images')
        user = self.request.user
        
        if user.is_authenticated:
            queryset = queryset.filter(Q(visibility=Visibility.PUBLIC) | Q(author=user))
            queryset = queryset.annotate(
                is_liked=Exists(GuideLike.objects.filter(user=user, guide=OuterRef('pk'))),
                is_scrapped=Exists(GuideScrap.objects.filter(user=user, guide=OuterRef('pk')))
            )
        else:
            queryset = queryset.filter(visibility=Visibility.PUBLIC)
            
        queryset = queryset.annotate(like_count=Count('likes', distinct=True), scrap_count=Count('scraps', distinct=True))

        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category: 
            queryset = queryset.filter(category=category.upper())
        if search: 
            queryset = queryset.filter(title__icontains=search)

        sort = self.request.query_params.get('sort', 'latest')
        if sort == 'most_scrapped': 
            queryset = queryset.order_by('-scrap_count', '-created_at')
        else: 
            queryset = queryset.order_by('-created_at')
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(response.data, dict) and "success" in response.data:
            return response
            
        if 200 <= response.status_code < 300:
            message = "요청이 성공적으로 처리되었습니다."
            if self.action == 'list': message = "설명서 목록 조회에 성공했습니다."
            elif self.action == 'retrieve': message = "설명서 상세 조회에 성공했습니다."
            elif self.action == 'create': message = "설명서가 성공적으로 등록되었습니다."
            elif self.action in ['update', 'partial_update']: message = "설명서가 성공적으로 수정되었습니다."
            elif self.action == 'destroy': 
                message = "설명서가 성공적으로 삭제되었습니다."
                response.data = None
            response.data = {"success": True, "data": response.data if response.data is not None else {}, "message": message}
            
        return response

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        guide = self.get_object()
        like, created = GuideLike.objects.get_or_create(user=request.user, guide=guide)
        if not created:
            like.delete()
            return Response({"success": True, "data": {"is_liked": False, "like_count": guide.likes.count()}, "message": "좋아요가 취소되었습니다."})
        return Response({"success": True, "data": {"is_liked": True, "like_count": guide.likes.count()}, "message": "좋아요가 등록되었습니다."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def scrap(self, request, pk=None):
        guide = self.get_object()
        scrap, created = GuideScrap.objects.get_or_create(user=request.user, guide=guide)
        if not created:
            scrap.delete()
            return Response({"success": True, "data": {"is_scrapped": False, "scrap_count": guide.scraps.count()}, "message": "스크랩이 취소되었습니다."})
        return Response({"success": True, "data": {"is_scrapped": True, "scrap_count": guide.scraps.count()}, "message": "스크랩이 등록되었습니다."})