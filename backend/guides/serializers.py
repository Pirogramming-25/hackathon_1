from rest_framework import serializers
from .models import Guide, GuideImage, Annotation

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = '__all__'

class GuideImageSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True, read_only=True) 

    class Meta:
        model = GuideImage
        fields = '__all__'

class GuideSerializer(serializers.ModelSerializer):
    images = GuideImageSerializer(many=True, read_only=True)

    class Meta:
        model = Guide
        fields = '__all__'
        read_only_fields = ['author', 'view_count', 'created_at', 'updated_at']