from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FamilyRelation


User = get_user_model()


class FamilyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "name"]


class FamilyRequestCreateSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField()

    def validate_target_user_id(self, value):
        request_user = self.context["request"].user
        if request_user.pk == value:
            raise serializers.ValidationError("자기 자신에게 가족 요청을 보낼 수 없습니다.")

        try:
            target_user = User.objects.get(pk=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("요청 대상 사용자를 찾을 수 없습니다.") from exc

        self.context["target_user"] = target_user
        return value


class FamilyRelationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    requester = FamilyUserSerializer(read_only=True)

    class Meta:
        model = FamilyRelation
        fields = [
            "id",
            "user",
            "requester",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_user(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        other_user = obj.other_user(request.user)
        if not other_user:
            return None
        return FamilyUserSerializer(other_user).data
