from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RoleChangeRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'bio', 'profile_picture', 'favorite_genres', 'is_approved')
        }),
    )
    list_display = ('username', 'email', 'role', 'is_approved', 'created_at')
    list_filter = ('role', 'is_approved', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(RoleChangeRequest)
class RoleChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_role', 'status', 'created_at')
    list_filter = ('status', 'requested_role', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Request Details', {
            'fields': ('requested_role', 'reason', 'status', 'admin_comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
