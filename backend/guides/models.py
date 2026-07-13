from django.db import models 
from django.conf import settings

class Category(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", "정부"
    FINANCE = "FINANCE", "금융"
    MEDICAL = "MEDICAL", "의료"
    LIFE = "LIFE", "생활"
    ETC = "ETC", "기타"

class Visibility(models.TextChoices):
    PUBLIC = 'public', '공개'
    PRIVATE = 'private', '비공개'

class Guide(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guides')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC) 
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class GuideImage(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='guides/%Y/%m/%d/')
    description = models.TextField(blank=True) 
    is_baked = models.BooleanField(default=False) 
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order']

class GuideLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) # 좋아요 누른 시간 저장!

    class Meta:
        unique_together = ('user', 'guide')

class GuideScrap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) # 스크랩한 시간 저장!

    class Meta:
        unique_together = ('user', 'guide')