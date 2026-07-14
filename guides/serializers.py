# guides/serializers.py
import os
from rest_framework import serializers
from django.db import transaction
from .models import Guide, GuideImage, GuideShare
from questions.models import Answer

class GuideImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideImage
        fields = ['id', 'image', 'description', 'is_baked', 'display_order']

class GuideSerializer(serializers.ModelSerializer):
    images = GuideImageSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')
    
    is_liked = serializers.BooleanField(read_only=True, default=False)
    is_scrapped = serializers.BooleanField(read_only=True, default=False)
    like_count = serializers.IntegerField(read_only=True, default=0)
    scrap_count = serializers.IntegerField(read_only=True, default=0)
    
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    # [수정] 설명 필드에 빈 문자열("") 허용 (allow_blank=True)
    uploaded_descriptions = serializers.ListField(
        child=serializers.CharField(allow_blank=True, required=False), 
        write_only=True, required=False
    )
    uploaded_is_baked = serializers.ListField(
        child=serializers.BooleanField(), write_only=True, required=False
    )

    class Meta:
        model = Guide
        fields = [
            'id', 'title', 'category', 'visibility', 'view_count',
            'created_at', 'updated_at', 'images', 'author', 
            'is_liked', 'is_scrapped', 'like_count', 'scrap_count',
            'uploaded_images', 'uploaded_descriptions', 'uploaded_is_baked'
        ]
        read_only_fields = ['view_count', 'created_at', 'updated_at']

    def validate(self, attrs):
        images = attrs.get('uploaded_images', [])
        descriptions = attrs.get('uploaded_descriptions', [])
        is_baked = attrs.get('uploaded_is_baked', [])
        
        # 1. 최대 이미지 개수 검증 (프론트엔드 기준 20장으로 동기화)
        if len(images) > 20:
            raise serializers.ValidationError({"uploaded_images": "이미지는 최대 20장까지만 등록할 수 있습니다."})
        
        # 2. 이미지, 설명, 가공 여부 배열 개수 일치 검증
        if images and (len(images) != len(descriptions) or len(images) != len(is_baked)):
            raise serializers.ValidationError("이미지, 설명, 가공 여부(is_baked)의 개수가 모두 일치해야 합니다.")

        # 3. 확장자 및 파일 크기 검증 (5MB 제한)
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        for img in images:
            ext = os.path.splitext(img.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError({"uploaded_images": f"지원하지 않는 확장자입니다: {ext}. (허용: jpg, jpeg, png, webp)"})
            if img.size > 5 * 1024 * 1024:
                raise serializers.ValidationError({"uploaded_images": "이미지 크기는 파일당 최대 5MB를 초과할 수 없습니다."})

        return attrs

    def _save_images(self, guide, images, descriptions, is_baked_list):
        for i, image in enumerate(images):
            desc = descriptions[i] if i < len(descriptions) else ""
            baked = is_baked_list[i] if i < len(is_baked_list) else False
            GuideImage.objects.create(
                guide=guide, 
                image=image, 
                description=desc, 
                is_baked=baked, 
                display_order=i + 1
            )

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images', [])
        descriptions = validated_data.pop('uploaded_descriptions', [])
        is_baked_list = validated_data.pop('uploaded_is_baked', [])
        
        with transaction.atomic():
            guide = Guide.objects.create(**validated_data)
            self._save_images(guide, images, descriptions, is_baked_list)
        return guide

    def update(self, instance, validated_data):
        images = validated_data.pop('uploaded_images', None)
        descriptions = validated_data.pop('uploaded_descriptions', [])
        is_baked_list = validated_data.pop('uploaded_is_baked', [])
        
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if images is not None:
                instance.images.all().delete()
                self._save_images(instance, images, descriptions, is_baked_list)
        return instance

# --------------------------------------------------------
# [수정] 답변 승격 전용 시리얼라이저
# 업로드 필드를 완전히 배제하여 500 에러를 원천 차단합니다.
# --------------------------------------------------------
class GuidePromoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = ["id", "title", "category", "visibility"]

    def create(self, validated_data):
        answer = self.context["answer"]

        with transaction.atomic():
            guide = Guide.objects.create(
                source_answer=answer,
                **validated_data,
            )

            answer_images = list(
                answer.images.all().order_by("display_order")
            )

            if answer_images:
                for index, answer_image in enumerate(answer_images, start=1):
                    image_description = answer_image.description.strip()

                    if index == 1:
                        description_parts = [
                            value
                            for value in [
                                answer.content.strip(),
                                image_description,
                            ]
                            if value
                        ]
                        description = "\n\n".join(description_parts)
                    else:
                        description = image_description

                    guide_image = GuideImage(
                        guide=guide,
                        description=description,
                        display_order=index,
                        is_baked=False,
                    )

                    file_name = os.path.basename(answer_image.image.name)

                    guide_image.image.save(
                        file_name,
                        answer_image.image.file,
                        save=True,
                    )

            else:
                GuideImage.objects.create(
                    guide=guide,
                    image=None,
                    description=answer.content.strip(),
                    display_order=1,
                    is_baked=False,
                )

        return guide

# --------------------------------------------------------
# [추가] 가족 공유 내역 반환용 시리얼라이저
# --------------------------------------------------------
class GuideShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideShare
        fields = ['id', 'recipient', 'created_at']