# guides/permissions.py
from rest_framework import permissions
from django.db.models import Q

from families.models import FamilyRelation
from .models import Visibility

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    디지털 설명서 플랫폼의 기획 권한 규칙을 강제합니다.
    1. 비로그인 유저: 조회(SAFE_METHODS)만 가능, 작성/수정/삭제/좋아요/스크랩 절대 불가
    2. 로그인 유저: 본인 글 수정/삭제 가능, 공개 글 조회 가능
    """

    def has_permission(self, request, view):
        # 조회 목적의 안전한 메서드는 누구나 통과 (단, 비공개 글은 아래 object 레벨에서 차단)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 작성(POST), 수정(PUT/PATCH), 삭제(DELETE)는 반드시 로그인(인증)된 유저만 가능
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. 조회(GET) 요청인 경우
        if request.method in permissions.SAFE_METHODS:
            # 공개글이면 누구나 볼 수 있음
            if obj.visibility == Visibility.PUBLIC:
                return True
            if obj.author == request.user:
                return True

            if not request.user.is_authenticated:
                return False

            # 수락된 가족 관계라면 작성자의 비공개 설명서도 조회 가능
            return FamilyRelation.objects.filter(
                Q(user1=request.user, user2=obj.author)
                | Q(user1=obj.author, user2=request.user),
                status=FamilyRelation.Status.ACCEPTED,
            ).exists()

        # 2. 수정/삭제(PUT, PATCH, DELETE) 요청인 경우 무조건 작성자 본인만 가능
        return obj.author == request.user
