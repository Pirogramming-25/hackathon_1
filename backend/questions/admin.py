
from django.contrib import admin

from .models import Answer, AnswerImage, Question, QuestionImage


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 1


class AnswerImageInline(admin.TabularInline):
    model = AnswerImage
    extra = 1


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    fields = ("author", "content", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "status", "created_at")
    list_filter = ("category", "status")
    search_fields = ("title", "content", "author__username", "author__email")
    inlines = [QuestionImageInline, AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "created_at")
    search_fields = ("content", "author__username", "author__email")
    inlines = [AnswerImageInline]