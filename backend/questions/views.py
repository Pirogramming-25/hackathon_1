# backend/questions/views.py

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Answer, Question
from .permissions import IsAnswerAuthor, IsAnswerAuthorForGuideData, IsQuestionAuthor
from .serializers import (
    AnswerCreateUpdateSerializer,
    GuideDataSerializer,
    QuestionCreateUpdateSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionStatusSerializer,
)


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


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return QuestionListSerializer
        if self.action == "retrieve":
            return QuestionDetailSerializer
        if self.action == "status_update":
            return QuestionStatusSerializer
        if self.action == "answers":
            return AnswerCreateUpdateSerializer
        return QuestionCreateUpdateSerializer

    def get_permissions(self):
        # 수정/삭제/상태변경만 작성자 검증, 나머지(list/retrieve/create/answers)는 로그인만 요구
        if self.action in ["update", "partial_update", "destroy", "status_update"]:
            return [IsAuthenticated(), IsQuestionAuthor()]
        return [IsAuthenticated()]

    # ---------- 목록 / 등록 ----------

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data).data
        return success_response(paginated_data, "질문 목록을 조회했습니다.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error_response("입력값을 확인해주세요.", data=serializer.errors)
        question = serializer.save()
        result = QuestionDetailSerializer(question, context={"request": request}).data
        return success_response(result, "질문이 등록되었습니다.", status.HTTP_201_CREATED)

    # ---------- 상세 / 수정 / 삭제 ----------

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return success_response(serializer.data, "질문을 조회했습니다.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )
        if not serializer.is_valid():
            return error_response("입력값을 확인해주세요.", data=serializer.errors)
        question = serializer.save()
        result = QuestionDetailSerializer(question, context={"request": request}).data
        return success_response(result, "질문이 수정되었습니다.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response({}, "질문이 삭제되었습니다.")

    # ---------- 상태 변경 ----------

    @action(detail=True, methods=["patch"], url_path="status")
    def status_update(self, request, pk=None):
        question = self.get_object()  # IsQuestionAuthor 검증 포함
        serializer = self.get_serializer(question, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response("입력값을 확인해주세요.", data=serializer.errors)
        question = serializer.save()
        result = QuestionStatusSerializer(question).data
        return success_response(result, "질문 상태가 변경되었습니다.")

    # ---------- 답변 등록 (질문에 종속) ----------

    @action(
        detail=True,
        methods=["post"],
        url_path="answers",
        permission_classes=[IsAuthenticated],
    )
    def answers(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)

        if question.status == Question.Status.RESOLVED:
            return error_response(
                "해결 완료된 질문에는 답변을 등록할 수 없습니다.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnswerCreateUpdateSerializer(
            data=request.data,
            context={"request": request, "question": question},
        )
        if not serializer.is_valid():
            return error_response("입력값을 확인해주세요.", data=serializer.errors)
        answer = serializer.save()
        from .serializers import AnswerSerializer

        result = AnswerSerializer(answer, context={"request": request}).data
        return success_response(result, "답변이 등록되었습니다.", status.HTTP_201_CREATED)


class AnswerViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Answer.objects.all()
    serializer_class = AnswerCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAnswerAuthor]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )
        if not serializer.is_valid():
            return error_response("입력값을 확인해주세요.", data=serializer.errors)
        answer = serializer.save()
        from .serializers import AnswerSerializer

        result = AnswerSerializer(answer, context={"request": request}).data
        return success_response(result, "답변이 수정되었습니다.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response({}, "답변이 삭제되었습니다.")

    @action(
        detail=True,
        methods=["get"],
        url_path="guide-data",
        permission_classes=[IsAuthenticated, IsAnswerAuthorForGuideData],
    )
    def guide_data(self, request, pk=None):
        answer = self.get_object()
        serializer = GuideDataSerializer(answer, context={"request": request})
        return success_response(serializer.data, "설명서 작성용 데이터를 조회했습니다.")