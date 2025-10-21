from django.contrib import admin
from .models import ScheduledPost, PostingSchedule, PostAnalytics


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'platform', 'scheduled_time', 'status', 'created_at']
    list_filter = ['status', 'platform', 'scheduled_time', 'created_at']
    search_fields = ['user__username', 'caption', 'hashtags']
    readonly_fields = ['created_at', 'updated_at', 'posted_at']
    date_hierarchy = 'scheduled_time'
    
    fieldsets = (
        ('User & Image', {
            'fields': ('user', 'image')
        }),
        ('Scheduling', {
            'fields': ('scheduled_time', 'platform', 'status')
        }),
        ('Content', {
            'fields': ('caption', 'hashtags')
        }),
        ('Publishing Details', {
            'fields': ('posted_at', 'platform_post_id', 'platform_post_url', 'error_message')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['cancel_posts', 'mark_as_failed']
    
    def cancel_posts(self, request, queryset):
        count = 0
        for post in queryset:
            if post.cancel():
                count += 1
        self.message_user(request, f'{count} posts annulés.')
    cancel_posts.short_description = 'Annuler les posts sélectionnés'
    
    def mark_as_failed(self, request, queryset):
        count = queryset.update(status='failed')
        self.message_user(request, f'{count} posts marqués comme échoués.')
    mark_as_failed.short_description = 'Marquer comme échoués'


@admin.register(PostingSchedule)
class PostingScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frequency', 'time_of_day', 'is_active', 'created_at']
    list_filter = ['frequency', 'is_active', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Schedule Configuration', {
            'fields': ('frequency', 'time_of_day', 'weekday', 'day_of_month')
        }),
        ('Platforms', {
            'fields': ('platforms',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['scheduled_post', 'likes', 'comments', 'shares', 'engagement_rate', 'last_synced_at']
    list_filter = ['last_synced_at', 'created_at']
    search_fields = ['scheduled_post__caption']
    readonly_fields = ['created_at', 'last_synced_at', 'engagement_rate']
    
    fieldsets = (
        ('Post', {
            'fields': ('scheduled_post',)
        }),
        ('Engagement Metrics', {
            'fields': ('likes', 'comments', 'shares', 'views')
        }),
        ('Reach Metrics', {
            'fields': ('reach', 'impressions', 'engagement_rate')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_synced_at'),
            'classes': ('collapse',)
        }),
    )
