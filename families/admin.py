from django.contrib import admin

from .models import FamilyRelation


@admin.register(FamilyRelation)
class FamilyRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "requester", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("user1__username", "user2__username", "requester__username")
