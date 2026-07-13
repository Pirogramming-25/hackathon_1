from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsQuestionAuthor(BasePermission):
    """
    질문 객체에 대해:
    - 조회(GET)는 로그인한 모든 사용자 허용 (IsAuthenticated와 함께 사용 전제)
    - 수정/삭제/상태변경은 작성자만 허용
    """

    message = "질문 작성자만 수정할 수 있습니다."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAnswerAuthor(BasePermission):
    """
    답변 객체에 대해:
    - 조회(GET)는 로그인한 모든 사용자 허용
    - 수정/삭제는 작성자만 허용
    """

    message = "답변 작성자만 수정할 수 있습니다."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAnswerAuthorForGuideData(BasePermission):
    """
    guide-data 조회는 '설명서 작성용으로 선택된 답변'의 작성자만 가능
    (SAFE_METHODS 예외 없음, 선택 안 된 답변은 작성자 본인도 접근 불가)
    """

    message = "설명서 작성용으로 선택된 답변만 데이터를 조회할 수 있습니다."

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user and obj.is_accepted

class IsQuestionAuthorOfAnswer(BasePermission):
    """
    답변을 '설명서 작성용으로 선택'하는 권한은 그 답변이 달린 질문의 작성자만 가능
    (IsAnswerAuthor와 다름 — 답변 작성자가 아니라 질문 작성자를 검사)
    """

    message = "질문 작성자만 답변을 선택할 수 있습니다."

    def has_object_permission(self, request, view, obj):
        return obj.question.author == request.user
