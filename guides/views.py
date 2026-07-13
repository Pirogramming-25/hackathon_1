# guides/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.db.models import Q, Count, Exists, OuterRef
from django.contrib.auth import get_user_model

# 모델 및 시리얼라이저 임포트 (공유 모델 포함)
from .models import Guide, Visibility, GuideLike, GuideScrap, GuideShare
from .serializers import GuideSerializer, GuidePromoteSerializer, GuideShareSerializer
from .permissions import IsAuthorOrReadOnly
from questions.models import Answer 
from families.models import FamilyRelation  # ✅ 방금 수정한 families 앱의 가족 관계 모델

User = get_user_model()

class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = [IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    # --------------------------------------------------------
    # 1. 답변 승격 API
    # --------------------------------------------------------
    @action(detail=False, methods=['post'], url_path=r'answers/(?P<answer_id>\d+)/promote')
    def promote_answer(self, request, answer_id=None):
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response({"success": False, "data": None, "message": "존재하지 않는 답변입니다."}, status=status.HTTP_404_NOT_FOUND)

        # [핵심 1] 권한 체크: '답변 작성자'가 아니라 '질문 작성자'인지 확인
        if answer.question.author != request.user:
            return Response({
                "success": False, "data": None, "message": "질문 작성자만 답변을 설명서로 승격할 수 있습니다."
            }, status=status.HTTP_403_FORBIDDEN)

        # [핵심 2] 1개 제한: 이 질문에 이미 승격된 설명서가 있는지 확인 (여러 답변 중 하나만 선택 방어)
        if Guide.objects.filter(source_answer__question=answer.question).exists():
            return Response({
                "success": False, "data": None, "message": "이 질문에서는 이미 설명서로 승격된 답변이 존재합니다. (하나만 선택 가능)"
            }, status=status.HTTP_409_CONFLICT)

        serializer = GuidePromoteSerializer(
            data=request.data, 
            context={'request': request, 'answer': answer}
        )
        
        if serializer.is_valid():
            
            guide = serializer.save(author=request.user) 
            
            return Response({"success": True, "data": serializer.data, "message": "성공적으로 승격되었습니다."}, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "data": serializer.errors, "message": "잘못된 입력값입니다."}, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------
    # 2. 공유 관리 API (GET, POST)
    # --------------------------------------------------------
    @action(detail=True, methods=['get', 'post'], url_path=r'shares(?:/(?P<user_id>\d+))?')
    def shares(self, request, pk=None, user_id=None):
        guide = self.get_object()
        
        if guide.author != request.user:
            return Response({"success": False, "data": None, "message": "설명서 작성자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
            
        if guide.visibility != Visibility.PRIVATE:
            return Response({"success": False, "data": None, "message": "PRIVATE 설명서만 공유할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # GET: 공유 목록 조회
        if request.method == 'GET':
            shares = GuideShare.objects.filter(guide=guide)
            serializer = GuideShareSerializer(shares, many=True)
            return Response({"success": True, "data": serializer.data, "message": "공유 목록 조회 성공"})

        # POST: 공유 추가
        elif request.method == 'POST':
            target_user_id = request.data.get('user_id') or user_id
            if not target_user_id:
                return Response({"success": False, "data": None, "message": "공유할 대상의 user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
                
            if str(target_user_id) == str(request.user.id):
                return Response({"success": False, "data": None, "message": "자신에게 공유할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                recipient = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return Response({"success": False, "data": None, "message": "대상을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 가족 연동 모델(FamilyRelation)에서 ACCEPTED 상태인지 검증
            is_family = FamilyRelation.objects.filter(
                Q(user1=request.user, user2=recipient) | Q(user1=recipient, user2=request.user), 
                status=FamilyRelation.Status.ACCEPTED
            ).exists()
            
            if not is_family:
                return Response({"success": False, "data": None, "message": "가족 관계가 수락(ACCEPTED)된 사용자에게만 공유할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            share, created = GuideShare.objects.get_or_create(guide=guide, recipient=recipient)
            if not created:
                return Response({"success": False, "data": None, "message": "이미 공유된 사용자입니다."}, status=status.HTTP_409_CONFLICT)
                
            return Response({"success": True, "data": GuideShareSerializer(share).data, "message": "공유되었습니다."}, status=status.HTTP_201_CREATED)

    # --------------------------------------------------------
    # 3. 공유 해제 API (DELETE)
    # --------------------------------------------------------
    @shares.mapping.delete
    def delete_share(self, request, pk=None, user_id=None):
        guide = self.get_object()
        
        if guide.author != request.user:
            return Response({"success": False, "data": None, "message": "설명서 작성자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
            
        if not user_id:
            return Response({"success": False, "data": None, "message": "공유를 해제할 대상의 user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
            
        share = GuideShare.objects.filter(guide=guide, recipient_id=user_id).first()
        if not share:
            return Response({"success": False, "data": None, "message": "공유 내역이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            
        share.delete()
        return Response({"success": True, "data": None, "message": "공유가 해제되었습니다."}, status=status.HTTP_200_OK)

    # --------------------------------------------------------
    # 4. 공통 쿼리셋 (조회, 목록 필터링)
    # --------------------------------------------------------
    def get_queryset(self):
        queryset = Guide.objects.select_related('author').prefetch_related('images')
        user = self.request.user
        
        if user.is_authenticated:
            # PUBLIC + 본인작성 + 내가 공유받은(shares__recipient=user) PRIVATE 글 모두 포함
            queryset = queryset.filter(
                Q(visibility=Visibility.PUBLIC) | 
                Q(author=user) | 
                Q(shares__recipient=user)
            ).distinct()
            
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

    # --------------------------------------------------------
    # 5. 기타 기본 뷰셋 오버라이딩 (생성, 조회수, 공통응답)
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # 6. 좋아요 & 스크랩 토글 API
    # --------------------------------------------------------
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