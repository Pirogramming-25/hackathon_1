# guides/models.py
from django.db import models 
from django.conf import settings

class Category(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", "정부"
    FINANCE = "FINANCE", "금융"
    MEDICAL = "MEDICAL", "의료"
    LIFE = "LIFE", "생활"
    ETC = "ETC", "기타"

class Visibility(models.TextChoices):
    PUBLIC = "PUBLIC", "공개"
    PRIVATE = "PRIVATE", "비공개"

class Guide(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guides')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC) 
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GuideImage(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='guides/')
    description = models.TextField(blank=True, help_text="단계별 설명") 
    is_baked = models.BooleanField(default=False, help_text="이미지 가공 여부") 
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order']
        constraints = [
            models.UniqueConstraint(fields=['guide', 'display_order'], name='unique_guide_image_order')
        ]

class GuideLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'guide'], name='unique_guide_like')]

class GuideScrap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='scraps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'guide'], name='unique_guide_scrap')]