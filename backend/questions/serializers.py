# backend/questions/serializers.py

from rest_framework import serializers

from .models import Answer, AnswerImage, Question, QuestionImage

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
MAX_IMAGE_SIZE_MB = 5


def validate_image_file(image):
    ext = image.name.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise serializers.ValidationError(
            f"지원하지 않는 이미지 형식입니다: {ext}"
        )
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise serializers.ValidationError(
            f"이미지 용량은 {MAX_IMAGE_SIZE_MB}MB를 초과할 수 없습니다."
        )


# ---------- 이미지 (읽기 전용) ----------

class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ["id", "image", "display_order"]


class AnswerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerImage
        fields = ["id", "image", "display_order"]


# ---------- 답변 (질문 상세에 중첩) ----------

class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    images = AnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "author",
            "content",
            "images",
            "created_at",
            "updated_at",
        ]


# ---------- 질문 목록 ----------

class QuestionListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    answer_count = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "author",
            "title",
            "category",
            "status",
            "created_at",
            "answer_count",
            "thumbnail",
        ]

    def get_answer_count(self, obj):
        return obj.answers.count()

    def get_thumbnail(self, obj):
        first_image = obj.images.order_by("display_order").first()
        if not first_image:
            return None
        request = self.context.get("request")
        url = first_image.image.url
        return request.build_absolute_uri(url) if request else url


# ---------- 질문 상세 ----------

class QuestionDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "author",
            "title",
            "content",
            "category",
            "status",
            "created_at",
            "updated_at",
            "images",
            "answers",
        ]


# ---------- 질문 생성·수정 ----------

class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Question
        fields = ["title", "content", "category", "images"]

    def validate_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError(
                "이미지는 최대 5장까지 등록할 수 있습니다."
            )
        for image in value:
            validate_image_file(image)
        return value

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        author = self.context["request"].user
        question = Question.objects.create(author=author, **validated_data)
        self._save_images(question, images)
        return question

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 방식 A: 새 이미지가 오면 기존 이미지 전체 삭제 후 재저장
        if images is not None:
            instance.images.all().delete()
            self._save_images(instance, images)

        return instance

    def _save_images(self, question, images):
        for order, image in enumerate(images, start=1):
            QuestionImage.objects.create(
                question=question, image=image, display_order=order
            )


# ---------- 질문 상태 변경 ----------

class QuestionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["status"]


# ---------- 답변 생성·수정 ----------

class AnswerCreateUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Answer
        fields = ["content", "images"]

    def validate_images(self, value):
        if len(value) > 4:
            raise serializers.ValidationError(
                "이미지는 최대 4장까지 등록할 수 있습니다."
            )
        for image in value:
            validate_image_file(image)
        return value

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        author = self.context["request"].user
        question = self.context["question"]
        answer = Answer.objects.create(
            author=author, question=question, **validated_data
        )
        self._save_images(answer, images)
        return answer

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images is not None:
            instance.images.all().delete()
            self._save_images(instance, images)

        return instance

    def _save_images(self, answer, images):
        for order, image in enumerate(images, start=1):
            AnswerImage.objects.create(
                answer=answer, image=image, display_order=order
            )


# ---------- 답변 → 설명서 작성용 데이터 ----------

class GuideImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AnswerImage
        fields = ["image_url", "display_order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class GuideDataSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField(source="id", read_only=True)
    category = serializers.CharField(source="question.category", read_only=True)
    images = GuideImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["answer_id", "category", "content", "images"]