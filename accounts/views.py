from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UIModeSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


User = get_user_model()


def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
    body = {
        "success": success,
        "data": data,
        "message": message,
    }
    return Response(body, status=status_code)


class CheckUsernameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        username = request.query_params.get("username", "").strip()
        if not username:
            return api_response(
                False,
                "아이디를 입력해주세요.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        exists = User.objects.filter(username=username).exists()
        return api_response(
            True,
            "아이디 중복 확인이 완료되었습니다.",
            {
                "username": username,
                "exists": exists,
                "available": not exists,
            },
        )


class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email", "").strip()
        if not email:
            return api_response(
                False,
                "이메일을 입력해주세요.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        exists = User.objects.filter(email=email).exists()
        return api_response(
            True,
            "이메일 중복 확인이 완료되었습니다.",
            {
                "email": email,
                "exists": exists,
                "available": not exists,
            },
        )


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                False,
                "회원가입에 실패했습니다.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        return api_response(
            True,
            "회원가입이 완료되었습니다.",
            UserSerializer(user).data,
            status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                False,
                "로그인에 실패했습니다.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return api_response(
                False,
                "아이디 또는 비밀번호가 올바르지 않습니다.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return api_response(
            True,
            "로그인되었습니다.",
            UserSerializer(user).data,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return api_response(True, "로그아웃되었습니다.")


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(
            True,
            "내 정보 조회가 완료되었습니다.",
            UserSerializer(request.user).data,
        )

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return api_response(
                False,
                "내 정보 수정에 실패했습니다.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
            )

        password_will_change = bool(serializer.validated_data.get("new_password"))
        user = serializer.save()
        if password_will_change:
            update_session_auth_hash(request, user)

        return api_response(
            True,
            "내 정보가 수정되었습니다.",
            UserSerializer(user).data,
        )


class UIModeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UIModeSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return api_response(
                False,
                "화면 모드 변경에 실패했습니다.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        return api_response(
            True,
            "화면 모드가 변경되었습니다.",
            UserSerializer(user).data,
        )
