from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'instagram_username', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['auto_validate_images', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'avatar', 'phone_number')
        }),
        ('Social Media', {
            'fields': ('instagram_username', 'facebook_page_id', 'twitter_username')
        }),
        ('Preferences', {
            'fields': ('default_image_style', 'auto_validate_images')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
