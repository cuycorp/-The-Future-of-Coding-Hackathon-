from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.images.models import GeneratedImage


class ScheduledPost(models.Model):
    """
    Model for scheduled social media posts
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifié'),
        ('processing', 'En cours de publication'),
        ('posted', 'Publié'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_posts')
    image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE, related_name='scheduled_posts')
    
    # Scheduling details
    scheduled_time = models.DateTimeField(help_text="Date et heure de publication prévue")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # Post content
    caption = models.TextField(max_length=2200, help_text="Légende du post")
    hashtags = models.TextField(blank=True, help_text="Hashtags (séparés par des espaces)")
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    posted_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Platform-specific data
    platform_post_id = models.CharField(max_length=200, blank=True, help_text="ID du post sur la plateforme")
    platform_post_url = models.URLField(max_length=500, blank=True, help_text="URL du post publié")
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduled_posts'
        verbose_name = 'Scheduled Post'
        verbose_name_plural = 'Scheduled Posts'
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['user', 'scheduled_time']),
            models.Index(fields=['status', 'scheduled_time']),
            models.Index(fields=['platform']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.scheduled_time}"

    @property
    def is_due(self):
        """Check if the post is due for publishing"""
        return self.scheduled_time <= timezone.now() and self.status == 'scheduled'

    @property
    def can_be_cancelled(self):
        """Check if the post can be cancelled"""
        return self.status in ['scheduled', 'failed']

    @property
    def is_published(self):
        """Check if the post has been published"""
        return self.status == 'posted'

    def cancel(self):
        """Cancel the scheduled post"""
        if self.can_be_cancelled:
            self.status = 'cancelled'
            self.save()
            return True
        return False


class PostingSchedule(models.Model):
    """
    Model for recurring posting schedules
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posting_schedules')
    name = models.CharField(max_length=100, help_text="Nom du planning")
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    time_of_day = models.TimeField(help_text="Heure de publication")
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text="Jour de la semaine (pour planning hebdomadaire)"
    )
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Jour du mois (pour planning mensuel, 1-31)"
    )
    
    # Platforms
    platforms = models.JSONField(
        default=list,
        help_text="Liste des plateformes pour ce planning"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posting_schedules'
        verbose_name = 'Posting Schedule'
        verbose_name_plural = 'Posting Schedules'
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PostAnalytics(models.Model):
    """
    Model for tracking post analytics and performance
    """
    scheduled_post = models.OneToOneField(
        ScheduledPost,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    # Engagement metrics
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    
    # Reach metrics
    reach = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    
    # Engagement rate
    engagement_rate = models.FloatField(default=0.0)
    
    # Last updated
    last_synced_at = models.DateTimeField(auto_now=True)
    
    # Raw data from platform
    raw_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_analytics'
        verbose_name = 'Post Analytics'
        verbose_name_plural = 'Post Analytics'

    def __str__(self):
        return f"Analytics for {self.scheduled_post}"

    def calculate_engagement_rate(self):
        """Calculate engagement rate"""
        if self.impressions > 0:
            total_engagement = self.likes + self.comments + self.shares
            self.engagement_rate = (total_engagement / self.impressions) * 100
            self.save()
        return self.engagement_rate
