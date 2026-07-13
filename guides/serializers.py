# guides/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Guide, GuideImage
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
    
    uploaded_images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    uploaded_descriptions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    uploaded_is_baked = serializers.ListField(child=serializers.BooleanField(), write_only=True, required=False)

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
        if len(images) > 30:
            raise serializers.ValidationError({"uploaded_images": "이미지는 최대 30장까지만 등록할 수 있습니다."})
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

# 답변 승격용 시리얼라이저 (기존 logic 유지)
class GuidePromoteSerializer(GuideSerializer):
    class Meta(GuideSerializer.Meta):
        fields = GuideSerializer.Meta.fields # 추가 필드 없이 기본 필드만 사용

    def create(self, validated_data):
        # 뷰에서 전달받은 answer 객체를 이용
        answer = self.context.get('answer')
        
        with transaction.atomic():
            # Guide 생성
            guide = Guide.objects.create(**validated_data)
            
            # 답변 이미지 복사 로직
            answer_images = answer.images.all().order_by('display_order')
            for a_img in answer_images:
                g_img = GuideImage(
                    guide=guide, 
                    description=a_img.description, 
                    display_order=a_img.display_order,
                    is_baked=False
                )
                file_name = a_img.image.name.split('/')[-1]
                g_img.image.save(file_name, a_img.image.file, save=True)
        return guide