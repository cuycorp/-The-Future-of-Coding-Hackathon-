from django.db import models
from django.contrib.auth.models import User


class GeneratedImage(models.Model):
    """
    Model for storing generated images
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('generating', 'En cours de génération'),
        ('generated', 'Générée'),
        ('validated', 'Validée'),
        ('rejected', 'Rejetée'),
        ('failed', 'Échec'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    prompt = models.TextField(help_text="Description de l'image à générer")
    negative_prompt = models.TextField(blank=True, help_text="Éléments à éviter dans l'image")
    
    # Image storage
    image_url = models.URLField(max_length=500, blank=True, null=True)
    image_file = models.ImageField(upload_to='generated_images/%Y/%m/%d/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Generation parameters
    style = models.CharField(max_length=100, default='realistic')
    width = models.IntegerField(default=1024)
    height = models.IntegerField(default=1024)
    quality = models.CharField(max_length=20, default='standard')
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    generation_time = models.FloatField(null=True, blank=True, help_text="Temps de génération en secondes")
    
    # Validation
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'generated_images'
        verbose_name = 'Generated Image'
        verbose_name_plural = 'Generated Images'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.prompt[:50]}... ({self.status})"

    @property
    def is_validated(self):
        return self.status == 'validated'

    @property
    def is_ready_for_scheduling(self):
        return self.status in ['validated', 'generated']


class ImageTag(models.Model):
    """
    Model for image tags/categories
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image_tags'
        verbose_name = 'Image Tag'
        verbose_name_plural = 'Image Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class ImageTagRelation(models.Model):
    """
    Many-to-many relationship between images and tags
    """
    image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(ImageTag, on_delete=models.CASCADE, related_name='image_relations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image_tag_relations'
        unique_together = ['image', 'tag']
        verbose_name = 'Image Tag Relation'
        verbose_name_plural = 'Image Tag Relations'

    def __str__(self):
        return f"{self.image.id} - {self.tag.name}"


class ImageGenerationHistory(models.Model):
    """
    Model to track image generation history and statistics
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generation_history')
    image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    
    action = models.CharField(max_length=50)  # 'generated', 'validated', 'rejected', etc.
    details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image_generation_history'
        verbose_name = 'Image Generation History'
        verbose_name_plural = 'Image Generation Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
