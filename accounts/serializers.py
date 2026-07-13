from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "name", "birth_date", "ui_mode")
        read_only_fields = ("id", "username")


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "name",
            "birth_date",
            "password",
            "password_confirm",
            "ui_mode",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "name": {"required": True, "allow_blank": False},
            "birth_date": {"required": True},
            "ui_mode": {"required": False},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)
        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )

        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            name=attrs.get("name"),
            birth_date=attrs.get("birth_date"),
            ui_mode=attrs.get("ui_mode", User.UIMode.BASIC),
        )
        password_validation.validate_password(password, user)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class UIModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("ui_mode",)
