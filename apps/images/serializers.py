from rest_framework import serializers
from .models import GeneratedImage, ImageTag, ImageTagRelation, ImageGenerationHistory


class ImageTagSerializer(serializers.ModelSerializer):
    """
    Serializer for image tags
    """
    class Meta:
        model = ImageTag
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class GeneratedImageSerializer(serializers.ModelSerializer):
    """
    Serializer for generated images
    """
    user = serializers.StringRelatedField(read_only=True)
    tags = serializers.SerializerMethodField()
    image_url_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedImage
        fields = [
            'id', 'user', 'prompt', 'negative_prompt',
            'image_url', 'image_file', 'thumbnail', 'image_url_display',
            'status', 'error_message',
            'style', 'width', 'height', 'quality',
            'metadata', 'generation_time',
            'validated_at', 'validation_notes',
            'tags', 'is_validated', 'is_ready_for_scheduling',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'image_url', 'image_file', 'thumbnail',
            'status', 'error_message', 'generation_time',
            'validated_at', 'created_at', 'updated_at'
        ]

    def get_tags(self, obj):
        tag_relations = obj.tag_relations.select_related('tag').all()
        return [relation.tag.name for relation in tag_relations]

    def get_image_url_display(self, obj):
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
        return obj.image_url


class ImageGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer for image generation requests
    """
    prompt = serializers.CharField(
        required=True,
        max_length=2000,
        help_text="Description de l'image à générer"
    )
    negative_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
        help_text="Éléments à éviter dans l'image"
    )
    style = serializers.CharField(
        required=False,
        default='realistic',
        max_length=100
    )
    width = serializers.IntegerField(
        required=False,
        default=1024,
        min_value=256,
        max_value=2048
    )
    height = serializers.IntegerField(
        required=False,
        default=1024,
        min_value=256,
        max_value=2048
    )
    quality = serializers.ChoiceField(
        choices=['standard', 'hd'],
        default='standard',
        required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )


class ImageValidationSerializer(serializers.Serializer):
    """
    Serializer for image validation
    """
    action = serializers.ChoiceField(
        choices=['validate', 'reject'],
        required=True
    )
    validation_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )


class ImageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating image details
    """
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = GeneratedImage
        fields = ['prompt', 'negative_prompt', 'validation_notes', 'tags']

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            # Remove existing tags
            instance.tag_relations.all().delete()
            
            # Add new tags
            for tag_name in tags_data:
                tag, _ = ImageTag.objects.get_or_create(name=tag_name.lower())
                ImageTagRelation.objects.create(image=instance, tag=tag)
        
        return instance


class ImageGenerationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for image generation history
    """
    user = serializers.StringRelatedField(read_only=True)
    image_id = serializers.IntegerField(source='image.id', read_only=True)
    
    class Meta:
        model = ImageGenerationHistory
        fields = ['id', 'user', 'image_id', 'action', 'details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ImageStatisticsSerializer(serializers.Serializer):
    """
    Serializer for image generation statistics
    """
    total_images = serializers.IntegerField()
    pending_images = serializers.IntegerField()
    generated_images = serializers.IntegerField()
    validated_images = serializers.IntegerField()
    rejected_images = serializers.IntegerField()
    failed_images = serializers.IntegerField()
    average_generation_time = serializers.FloatField()
    total_generation_time = serializers.FloatField()
