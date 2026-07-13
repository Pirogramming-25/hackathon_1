from django.db import models 
from django.conf import settings

class Category(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", "정부"
    FINANCE = "FINANCE", "금융"
    MEDICAL = "MEDICAL", "의료"
    LIFE = "LIFE", "생활"
    ETC = "ETC", "기타"

class Guide(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guides')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    visibility = models.CharField(max_length=10, default='public') 
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # question = models.ForeignKey('questions.Question', on_delete=models.SET_NULL, null=True, blank=True, related_name='guides')

    def __str__(self):
        return self.title

class GuideImage(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='guides/%Y/%m/%d/')
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        unique_together = ['guide', 'display_order']

class Annotation(models.Model):
    guide_image = models.ForeignKey(GuideImage, on_delete=models.CASCADE, related_name='annotations')
    shape_type = models.CharField(max_length=50) 
    x_ratio = models.DecimalField(max_digits=7, decimal_places=6)
    y_ratio = models.DecimalField(max_digits=7, decimal_places=6)
    width_ratio = models.DecimalField(max_digits=7, decimal_places=6)
    height_ratio = models.DecimalField(max_digits=7, decimal_places=6)
    annotation_text = models.CharField(max_length=500, blank=True)
    display_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)