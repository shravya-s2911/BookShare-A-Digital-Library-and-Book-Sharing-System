from django.contrib import admin
from .models import Community, CommunityPost, Comment


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'community', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
