from django.contrib import admin
from .models import GeneratedImage, ImageTag, ImageTagRelation, ImageGenerationHistory


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prompt_preview', 'status', 'style', 'created_at']
    list_filter = ['status', 'style', 'quality', 'created_at']
    search_fields = ['user__username', 'prompt', 'validation_notes']
    readonly_fields = ['created_at', 'updated_at', 'validated_at', 'generation_time']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User & Status', {
            'fields': ('user', 'status', 'error_message')
        }),
        ('Prompt', {
            'fields': ('prompt', 'negative_prompt')
        }),
        ('Image Files', {
            'fields': ('image_url', 'image_file', 'thumbnail')
        }),
        ('Generation Parameters', {
            'fields': ('style', 'width', 'height', 'quality', 'generation_time')
        }),
        ('Validation', {
            'fields': ('validated_at', 'validation_notes')
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
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'


@admin.register(ImageTag)
class ImageTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'image_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def image_count(self, obj):
        return obj.image_relations.count()
    image_count.short_description = 'Images'


@admin.register(ImageTagRelation)
class ImageTagRelationAdmin(admin.ModelAdmin):
    list_display = ['image', 'tag', 'created_at']
    list_filter = ['tag', 'created_at']
    search_fields = ['image__prompt', 'tag__name']
    readonly_fields = ['created_at']


@admin.register(ImageGenerationHistory)
class ImageGenerationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'image', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'action']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'image', 'action')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
