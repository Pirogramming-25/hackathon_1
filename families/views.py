from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FamilyRelation
from .serializers import (
    FamilyRelationSerializer,
    FamilyRequestCreateSerializer,
    FamilyUserSerializer,
)


User = get_user_model()


def success_response(data, message, status_code=status.HTTP_200_OK):
    return Response(
        {"success": True, "data": data, "message": message},
        status=status_code,
    )


def error_response(message, data=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {"success": False, "data": data, "message": message},
        status=status_code,
    )


def get_ordered_users(user_a, user_b):
    return (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)


class FamilyUserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.query_params.get("username", "").strip()
        queryset = User.objects.exclude(pk=request.user.pk).order_by("username")

        if username:
            queryset = queryset.filter(username__icontains=username)
        else:
            queryset = queryset.none()

        serializer = FamilyUserSerializer(queryset, many=True)
        return success_response(
            serializer.data,
            "사용자 검색 결과를 조회했습니다.",
        )


class FamilyRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = FamilyRequestCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return error_response("가족 요청에 실패했습니다.", serializer.errors)

        requester = request.user
        target_user = serializer.context["target_user"]
        user1, user2 = get_ordered_users(requester, target_user)

        relation = (
            FamilyRelation.objects.select_for_update()
            .filter(user1=user1, user2=user2)
            .first()
        )

        if relation and relation.status in {
            FamilyRelation.Status.PENDING,
            FamilyRelation.Status.ACCEPTED,
        }:
            return error_response("이미 가족 요청 또는 가족 관계가 존재합니다.")

        if relation:
            relation.status = FamilyRelation.Status.PENDING
            relation.requester = requester
            relation.save(update_fields=["status", "requester", "updated_at"])
            status_code = status.HTTP_200_OK
        else:
            relation = FamilyRelation.objects.create(
                user1=user1,
                user2=user2,
                requester=requester,
                status=FamilyRelation.Status.PENDING,
            )
            status_code = status.HTTP_201_CREATED

        return success_response(
            FamilyRelationSerializer(relation, context={"request": request}).data,
            "가족 요청을 보냈습니다.",
            status_code,
        )


class ReceivedFamilyRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = FamilyRelation.objects.filter(
            status=FamilyRelation.Status.PENDING,
        ).filter(
            Q(user1=request.user) | Q(user2=request.user),
        ).exclude(requester=request.user)

        serializer = FamilyRelationSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return success_response(
            serializer.data,
            "받은 가족 요청 목록을 조회했습니다.",
        )


class SentFamilyRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = FamilyRelation.objects.filter(
            requester=request.user,
            status=FamilyRelation.Status.PENDING,
        )

        serializer = FamilyRelationSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return success_response(
            serializer.data,
            "보낸 가족 요청 목록을 조회했습니다.",
        )


class FamilyRequestDecisionView(APIView):
    permission_classes = [IsAuthenticated]
    decision_status = None
    success_message = ""

    def patch(self, request, relation_id):
        relation = get_object_or_404(FamilyRelation, pk=relation_id)

        if not relation.is_participant(request.user):
            return error_response(
                "가족 요청의 당사자만 처리할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if relation.requester_id == request.user.pk:
            return error_response(
                "요청을 보낸 사용자는 해당 요청을 처리할 수 없습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if relation.status != FamilyRelation.Status.PENDING:
            return error_response("대기 중인 가족 요청만 처리할 수 있습니다.")

        relation.status = self.decision_status
        relation.save(update_fields=["status", "updated_at"])

        return success_response(
            FamilyRelationSerializer(relation, context={"request": request}).data,
            self.success_message,
        )


class FamilyRequestAcceptView(FamilyRequestDecisionView):
    decision_status = FamilyRelation.Status.ACCEPTED
    success_message = "가족 요청을 수락했습니다."


class FamilyRequestRejectView(FamilyRequestDecisionView):
    decision_status = FamilyRelation.Status.REJECTED
    success_message = "가족 요청을 거절했습니다."


class FamilyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = FamilyRelation.objects.filter(
            status=FamilyRelation.Status.ACCEPTED,
        ).filter(
            Q(user1=request.user) | Q(user2=request.user),
        )

        serializer = FamilyRelationSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return success_response(
            serializer.data,
            "연동된 가족 목록을 조회했습니다.",
        )


class FamilyRelationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, relation_id):
        relation = get_object_or_404(FamilyRelation, pk=relation_id)

        if not relation.is_participant(request.user):
            return error_response(
                "가족 관계의 당사자만 연동을 해제할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if relation.status != FamilyRelation.Status.ACCEPTED:
            return error_response("연동된 가족 관계만 해제할 수 있습니다.")

        relation.delete()
        return success_response(None, "가족 연동을 해제했습니다.")
