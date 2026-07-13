# guides/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.db.models import Q, Count, Exists, OuterRef

from .models import Guide, Visibility, GuideLike, GuideScrap
from .serializers import GuideSerializer
from .permissions import IsAuthorOrReadOnly

class GuideViewSet(viewsets.ModelViewSet):
    serializer_class = GuideSerializer
    permission_classes = [IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # 1. N+1 문제를 원천 차단하기 위한 관계형 테이블 Eager Loading
        queryset = Guide.objects.select_related('author').prefetch_related('images')
        user = self.request.user
        
        # 2. 기획 제약 조건: 비로그인은 오직 공개(PUBLIC), 로그인은 공개 + 본인 비공개(PRIVATE)만 조회
        if user.is_authenticated:
            queryset = queryset.filter(Q(visibility=Visibility.PUBLIC) | Q(author=user))
            queryset = queryset.annotate(
                is_liked=Exists(GuideLike.objects.filter(user=user, guide=OuterRef('pk'))),
                is_scrapped=Exists(GuideScrap.objects.filter(user=user, guide=OuterRef('pk')))
            )
        else:
            queryset = queryset.filter(visibility=Visibility.PUBLIC)
            
        # 3. 좋아요 수 및 스크랩 수 집계 연산 (정렬을 위해 미리 계산)
        queryset = queryset.annotate(
            like_count=Count('likes', distinct=True),
            scrap_count=Count('scraps', distinct=True)
        )

        # --------------------------------------------------
        # 4. 필터 기능 (카테고리, 검색어)
        # --------------------------------------------------
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            # 대소문자 상관없이 매칭되도록 upper() 처리
            queryset = queryset.filter(category=category.upper())
        if search:
            # 제목에 검색어가 포함되어 있는지 확인 (icontains: 대소문자 구분 없음)
            queryset = queryset.filter(title__icontains=search)

        # --------------------------------------------------
        # 5. 정렬 기능 (최신순, 스크랩 많은 순)
        # --------------------------------------------------
        sort = self.request.query_params.get('sort', 'latest') # 파라미터가 없으면 'latest' 기본값
        
        if sort == 'most_scrapped':
            # 스크랩 많은 순으로 먼저 정렬하고, 스크랩 수가 같으면 최신순으로 정렬
            queryset = queryset.order_by('-scrap_count', '-created_at')
        else:
            # 기본값 (latest): 최신순 정렬
            queryset = queryset.order_by('-created_at')
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """상세 조회 시 조회수(view_count) 안전 증가 처리"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # --------------------------------------------------
    # 팀 표준 가이드라인 적용: 공통 응답 자동 포맷팅 레이어
    # --------------------------------------------------
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # 이미 래핑되어 있거나 에러 응답(4xx, 5xx)인 경우는 패스
        if isinstance(response.data, dict) and "success" in response.data:
            return response
            
        if 200 <= response.status_code < 300:
            message = "요청이 성공적으로 처리되었습니다."
            if self.action == 'list':
                message = "설명서 목록 조회에 성공했습니다."
            elif self.action == 'retrieve':
                message = "설명서 상세 조회에 성공했습니다."
            elif self.action == 'create':
                message = "설명서가 성공적으로 등록되었습니다."
            elif self.action == 'update' or self.action == 'partial_update':
                message = "설명서가 성공적으로 수정되었습니다."
            elif self.action == 'destroy':
                message = "설명서가 성공적으로 삭제되었습니다."
                response.status_code = status.HTTP_200_OK
                # 기존의 response.data(빈 값) 대신 명시적으로 None(null) 주입
                response.data = None 

            response.data = {
                "success": True,
                "data": response.data, # 데이터가 None이면 JSON에서 null로 변환됨
                "message": message
            }

            response.data = {
                "success": True,
                "data": response.data if response.data is not None else {},
                "message": message
            }
        return response

    # --------------------------------------------------
    # 좋아요 기능 엔드포인트 분기 (POST: 등록 / DELETE: 취소)
    # --------------------------------------------------
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        guide = self.get_object()
        
        # get_or_create: DB에 있으면 가져오고(created=False), 없으면 새로 만듭니다(created=True)
        like, created = GuideLike.objects.get_or_create(user=request.user, guide=guide)
        
        if not created:
            # 이미 좋아요가 눌려 있던 상태라면 -> 삭제(취소) 처리
            like.delete()
            return Response({
                "success": True,
                "data": {"is_liked": False, "like_count": guide.likes.count()},
                "message": "좋아요가 취소되었습니다."
            })
            
        # 새로 만들어진 상태라면 -> 등록 처리
        return Response({
            "success": True,
            "data": {"is_liked": True, "like_count": guide.likes.count()},
            "message": "좋아요가 등록되었습니다."
        })

    # --------------------------------------------------
    # 스크랩 기능 엔드포인트 분기 (POST: 등록 / DELETE: 취소)
    # --------------------------------------------------
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def scrap(self, request, pk=None):
        guide = self.get_object()
        
        scrap, created = GuideScrap.objects.get_or_create(user=request.user, guide=guide)
        
        if not created:
            # 이미 스크랩이 되어 있던 상태라면 -> 삭제(취소) 처리
            scrap.delete()
            return Response({
                "success": True,
                "data": {"is_scrapped": False, "scrap_count": guide.scraps.count()},
                "message": "스크랩이 취소되었습니다."
            })
            
        return Response({
            "success": True,
            "data": {"is_scrapped": True, "scrap_count": guide.scraps.count()},
            "message": "스크랩이 등록되었습니다."
        })