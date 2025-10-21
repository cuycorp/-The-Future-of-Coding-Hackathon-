from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q
from .models import GeneratedImage, ImageTag, ImageGenerationHistory
from .serializers import (
    GeneratedImageSerializer,
    ImageGenerationRequestSerializer,
    ImageValidationSerializer,
    ImageUpdateSerializer,
    ImageTagSerializer,
    ImageGenerationHistorySerializer,
    ImageStatisticsSerializer
)
from .tasks import generate_image_task


class ImagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class GenerateImageView(APIView):
    """
    API endpoint to generate a new image
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ImageGenerationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create the image instance
            image = GeneratedImage.objects.create(
                user=request.user,
                prompt=serializer.validated_data['prompt'],
                negative_prompt=serializer.validated_data.get('negative_prompt', ''),
                style=serializer.validated_data.get('style', 'realistic'),
                width=serializer.validated_data.get('width', 1024),
                height=serializer.validated_data.get('height', 1024),
                quality=serializer.validated_data.get('quality', 'standard'),
                status='pending'
            )
            
            # Add tags if provided
            tags_data = serializer.validated_data.get('tags', [])
            for tag_name in tags_data:
                tag, _ = ImageTag.objects.get_or_create(name=tag_name.lower())
                image.tag_relations.create(tag=tag)
            
            # Trigger async image generation
            generate_image_task.delay(image.id)
            
            # Log the request
            ImageGenerationHistory.objects.create(
                user=request.user,
                image=image,
                action='requested',
                details=serializer.validated_data
            )
            
            return Response({
                'message': 'Génération d\'image lancée avec succès.',
                'image': GeneratedImageSerializer(image, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageListView(generics.ListAPIView):
    """
    API endpoint to list user's generated images
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GeneratedImageSerializer
    pagination_class = ImagePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prompt', 'validation_notes']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = GeneratedImage.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tag_relations__tag__name__in=tag_list).distinct()
        
        return queryset.select_related('user').prefetch_related('tag_relations__tag')


class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific image
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GeneratedImageSerializer

    def get_queryset(self):
        return GeneratedImage.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ImageUpdateSerializer
        return GeneratedImageSerializer

    def perform_destroy(self, instance):
        # Delete the actual files
        if instance.image_file:
            instance.image_file.delete(save=False)
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        
        # Log the deletion
        ImageGenerationHistory.objects.create(
            user=self.request.user,
            action='deleted',
            details={'image_id': instance.id, 'prompt': instance.prompt}
        )
        
        instance.delete()


class ValidateImageView(APIView):
    """
    API endpoint to validate or reject an image
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            image = GeneratedImage.objects.get(pk=pk, user=request.user)
        except GeneratedImage.DoesNotExist:
            return Response(
                {'error': 'Image non trouvée.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ImageValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            validation_notes = serializer.validated_data.get('validation_notes', '')
            
            if action == 'validate':
                image.status = 'validated'
                image.validated_at = timezone.now()
                message = 'Image validée avec succès.'
            else:  # reject
                image.status = 'rejected'
                message = 'Image rejetée.'
            
            image.validation_notes = validation_notes
            image.save()
            
            # Log the validation
            ImageGenerationHistory.objects.create(
                user=request.user,
                image=image,
                action=action,
                details={'notes': validation_notes}
            )
            
            return Response({
                'message': message,
                'image': GeneratedImageSerializer(image, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageStatisticsView(APIView):
    """
    API endpoint to get user's image generation statistics
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_images = GeneratedImage.objects.filter(user=request.user)
        
        stats = {
            'total_images': user_images.count(),
            'pending_images': user_images.filter(status='pending').count(),
            'generated_images': user_images.filter(status='generated').count(),
            'validated_images': user_images.filter(status='validated').count(),
            'rejected_images': user_images.filter(status='rejected').count(),
            'failed_images': user_images.filter(status='failed').count(),
        }
        
        # Calculate average generation time
        avg_time = user_images.filter(
            generation_time__isnull=False
        ).aggregate(Avg('generation_time'))['generation_time__avg']
        
        stats['average_generation_time'] = round(avg_time, 2) if avg_time else 0
        
        # Calculate total generation time
        total_time = user_images.filter(
            generation_time__isnull=False
        ).aggregate(Sum('generation_time'))['generation_time__sum']
        
        stats['total_generation_time'] = round(total_time, 2) if total_time else 0
        
        serializer = ImageStatisticsSerializer(stats)
        return Response(serializer.data)


class ImageTagListView(generics.ListCreateAPIView):
    """
    API endpoint to list and create image tags
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageTagSerializer
    queryset = ImageTag.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class ImageHistoryView(generics.ListAPIView):
    """
    API endpoint to view image generation history
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageGenerationHistorySerializer
    pagination_class = ImagePagination

    def get_queryset(self):
        return ImageGenerationHistory.objects.filter(
            user=self.request.user
        ).select_related('user', 'image').order_by('-created_at')
