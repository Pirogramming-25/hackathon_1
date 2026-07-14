from django.contrib import admin

from .models import Guide, GuideImage, GuideLike, GuideScrap, GuideShare


class GuideImageInline(admin.TabularInline):
    model = GuideImage
    extra = 0
    fields = (
        "image",
        "description",
        "is_baked",
        "display_order",
    )


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "category",
        "visibility",
        "view_count",
        "created_at",
    )
    list_filter = ("category", "visibility", "created_at")
    search_fields = (
        "title",
        "author__username",
        "author__email",
        "images__description",
    )
    readonly_fields = ("view_count", "created_at", "updated_at")
    list_select_related = ("author", "source_answer")
    inlines = [GuideImageInline]


@admin.register(GuideImage)
class GuideImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "guide",
        "display_order",
        "is_baked",
    )
    list_filter = ("is_baked",)
    search_fields = ("guide__title", "description")
    list_select_related = ("guide",)


@admin.register(GuideLike)
class GuideLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "guide", "user", "created_at")
    search_fields = ("guide__title", "user__username", "user__email")
    list_select_related = ("guide", "user")


@admin.register(GuideScrap)
class GuideScrapAdmin(admin.ModelAdmin):
    list_display = ("id", "guide", "user", "created_at")
    search_fields = ("guide__title", "user__username", "user__email")
    list_select_related = ("guide", "user")


@admin.register(GuideShare)
class GuideShareAdmin(admin.ModelAdmin):
    list_display = ("id", "guide", "recipient", "created_at")
    search_fields = (
        "guide__title",
        "recipient__username",
        "recipient__email",
    )
    list_select_related = ("guide", "recipient", "family_relation")
