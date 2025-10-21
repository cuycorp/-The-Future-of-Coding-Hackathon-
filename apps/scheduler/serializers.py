from rest_framework import serializers
from django.utils import timezone
from .models import ScheduledPost, PostingSchedule, PostAnalytics
from apps.images.serializers import GeneratedImageSerializer


class ScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for scheduled posts
    """
    user = serializers.StringRelatedField(read_only=True)
    image_details = GeneratedImageSerializer(source='image', read_only=True)
    is_due = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ScheduledPost
        fields = [
            'id', 'user', 'image', 'image_details',
            'scheduled_time', 'platform', 'caption', 'hashtags',
            'status', 'posted_at', 'error_message',
            'platform_post_id', 'platform_post_url',
            'metadata', 'is_due', 'can_be_cancelled', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'posted_at', 'error_message',
            'platform_post_id', 'platform_post_url',
            'created_at', 'updated_at'
        ]

    def validate_scheduled_time(self, value):
        """Validate that scheduled time is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError(
                "La date de planification doit être dans le futur."
            )
        return value

    def validate_image(self, value):
        """Validate that the image is ready for scheduling"""
        if not value.is_ready_for_scheduling:
            raise serializers.ValidationError(
                "L'image doit être validée avant d'être planifiée."
            )
        return value


class CreateScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating scheduled posts
    """
    class Meta:
        model = ScheduledPost
        fields = [
            'image', 'scheduled_time', 'platform',
            'caption', 'hashtags'
        ]

    def validate_scheduled_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "La date de planification doit être dans le futur."
            )
        return value

    def validate_image(self, value):
        # Check if user owns the image
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError(
                "Vous ne pouvez planifier que vos propres images."
            )
        
        if not value.is_ready_for_scheduling:
            raise serializers.ValidationError(
                "L'image doit être validée avant d'être planifiée."
            )
        return value


class UpdateScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for updating scheduled posts
    """
    class Meta:
        model = ScheduledPost
        fields = ['scheduled_time', 'caption', 'hashtags']

    def validate_scheduled_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "La date de planification doit être dans le futur."
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status not in ['scheduled', 'failed']:
            raise serializers.ValidationError(
                "Seuls les posts planifiés ou échoués peuvent être modifiés."
            )
        return attrs


class PostingScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for posting schedules
    """
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = PostingSchedule
        fields = [
            'id', 'user', 'name', 'frequency', 'time_of_day',
            'weekday', 'day_of_month', 'platforms', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        frequency = attrs.get('frequency')
        
        # Validate weekday for weekly frequency
        if frequency == 'weekly' and not attrs.get('weekday'):
            raise serializers.ValidationError({
                'weekday': 'Le jour de la semaine est requis pour un planning hebdomadaire.'
            })
        
        # Validate day_of_month for monthly frequency
        if frequency == 'monthly':
            day_of_month = attrs.get('day_of_month')
            if not day_of_month:
                raise serializers.ValidationError({
                    'day_of_month': 'Le jour du mois est requis pour un planning mensuel.'
                })
            if day_of_month < 1 or day_of_month > 31:
                raise serializers.ValidationError({
                    'day_of_month': 'Le jour du mois doit être entre 1 et 31.'
                })
        
        # Validate platforms
        platforms = attrs.get('platforms', [])
        if not platforms:
            raise serializers.ValidationError({
                'platforms': 'Au moins une plateforme doit être sélectionnée.'
            })
        
        valid_platforms = ['instagram', 'facebook', 'twitter', 'linkedin']
        for platform in platforms:
            if platform not in valid_platforms:
                raise serializers.ValidationError({
                    'platforms': f'Plateforme invalide: {platform}'
                })
        
        return attrs


class PostAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for post analytics
    """
    scheduled_post_id = serializers.IntegerField(source='scheduled_post.id', read_only=True)
    platform = serializers.CharField(source='scheduled_post.platform', read_only=True)
    
    class Meta:
        model = PostAnalytics
        fields = [
            'id', 'scheduled_post_id', 'platform',
            'likes', 'comments', 'shares', 'views',
            'reach', 'impressions', 'engagement_rate',
            'last_synced_at', 'created_at'
        ]
        read_only_fields = ['id', 'engagement_rate', 'last_synced_at', 'created_at']


class SchedulerStatisticsSerializer(serializers.Serializer):
    """
    Serializer for scheduler statistics
    """
    total_scheduled = serializers.IntegerField()
    total_posted = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    total_cancelled = serializers.IntegerField()
    upcoming_posts = serializers.IntegerField()
    posts_by_platform = serializers.DictField()
    average_engagement_rate = serializers.FloatField()
