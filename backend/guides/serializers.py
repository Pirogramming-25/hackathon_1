from rest_framework import serializers
from .models import Guide, GuideImage

class GuideImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideImage
        fields = ['id', 'image', 'description', 'is_baked', 'display_order']

class GuideSerializer(serializers.ModelSerializer):
    images = GuideImageSerializer(many=True, read_only=True)
    # 업로드용 필드
    uploaded_images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    uploaded_descriptions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    uploaded_is_baked = serializers.ListField(child=serializers.BooleanField(), write_only=True, required=False)

    class Meta:
        model = Guide
        fields = ['id', 'title', 'category', 'visibility', 'images', 'uploaded_images', 'uploaded_descriptions', 'uploaded_is_baked', 'author']
        read_only_fields = ['author']

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images', [])
        descriptions = validated_data.pop('uploaded_descriptions', [])
        is_baked_list = validated_data.pop('uploaded_is_baked', [])
        
        guide = Guide.objects.create(**validated_data)
        
        for i, image in enumerate(images):
            desc = descriptions[i] if i < len(descriptions) else ""
            baked = is_baked_list[i] if i < len(is_baked_list) else False
            GuideImage.objects.create(guide=guide, image=image, description=desc, is_baked=baked, display_order=i+1)
        return guide