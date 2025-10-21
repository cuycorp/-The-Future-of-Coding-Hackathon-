from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import ScheduledPost, PostingSchedule, PostAnalytics
from .serializers import (
    ScheduledPostSerializer,
    CreateScheduledPostSerializer,
    UpdateScheduledPostSerializer,
    PostingScheduleSerializer,
    PostAnalyticsSerializer,
    SchedulerStatisticsSerializer
)
from .tasks import publish_scheduled_post, sync_post_analytics


class SchedulerPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SchedulePostView(APIView):
    """
    API endpoint to schedule a new post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateScheduledPostSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            scheduled_post = serializer.save(user=request.user)
            
            return Response({
                'message': 'Post planifié avec succès.',
                'post': ScheduledPostSerializer(
                    scheduled_post,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduledPostListView(generics.ListAPIView):
    """
    API endpoint to list user's scheduled posts
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduledPostSerializer
    pagination_class = SchedulerPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['caption', 'hashtags']
    ordering_fields = ['scheduled_time', 'created_at', 'status']
    ordering = ['scheduled_time']

    def get_queryset(self):
        queryset = ScheduledPost.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by platform
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(scheduled_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_time__lte=end_date)
        
        return queryset.select_related('user', 'image')


class ScheduledPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a scheduled post
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduledPostSerializer

    def get_queryset(self):
        return ScheduledPost.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateScheduledPostSerializer
        return ScheduledPostSerializer

    def perform_destroy(self, instance):
        if not instance.can_be_cancelled:
            return Response(
                {'error': 'Ce post ne peut pas être annulé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.cancel()


class CancelScheduledPostView(APIView):
    """
    API endpoint to cancel a scheduled post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = ScheduledPost.objects.get(pk=pk, user=request.user)
        except ScheduledPost.DoesNotExist:
            return Response(
                {'error': 'Post non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.cancel():
            return Response({
                'message': 'Post annulé avec succès.',
                'post': ScheduledPostSerializer(post, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Ce post ne peut pas être annulé.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PublishNowView(APIView):
    """
    API endpoint to publish a scheduled post immediately
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = ScheduledPost.objects.get(pk=pk, user=request.user)
        except ScheduledPost.DoesNotExist:
            return Response(
                {'error': 'Post non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.status != 'scheduled':
            return Response(
                {'error': 'Seuls les posts planifiés peuvent être publiés immédiatement.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger immediate publishing
        task = publish_scheduled_post.delay(post.id)
        
        return Response({
            'message': 'Publication lancée.',
            'task_id': task.id,
            'post': ScheduledPostSerializer(post, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class PostingScheduleListView(generics.ListCreateAPIView):
    """
    API endpoint to list and create posting schedules
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostingScheduleSerializer
    pagination_class = SchedulerPagination

    def get_queryset(self):
        return PostingSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostingScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a posting schedule
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostingScheduleSerializer

    def get_queryset(self):
        return PostingSchedule.objects.filter(user=self.request.user)


class PostAnalyticsView(APIView):
    """
    API endpoint to get analytics for a scheduled post
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            post = ScheduledPost.objects.get(pk=pk, user=request.user)
        except ScheduledPost.DoesNotExist:
            return Response(
                {'error': 'Post non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.status != 'posted':
            return Response(
                {'error': 'Les analytics ne sont disponibles que pour les posts publiés.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            analytics = post.analytics
            serializer = PostAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except PostAnalytics.DoesNotExist:
            return Response(
                {'error': 'Analytics non disponibles pour ce post.'},
                status=status.HTTP_404_NOT_FOUND
            )


class SyncAnalyticsView(APIView):
    """
    API endpoint to sync analytics for a post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = ScheduledPost.objects.get(pk=pk, user=request.user)
        except ScheduledPost.DoesNotExist:
            return Response(
                {'error': 'Post non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.status != 'posted':
            return Response(
                {'error': 'Seuls les posts publiés peuvent avoir leurs analytics synchronisées.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger analytics sync
        task = sync_post_analytics.delay(post.id)
        
        return Response({
            'message': 'Synchronisation des analytics lancée.',
            'task_id': task.id
        }, status=status.HTTP_200_OK)


class SchedulerStatisticsView(APIView):
    """
    API endpoint to get scheduler statistics
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_posts = ScheduledPost.objects.filter(user=request.user)
        
        stats = {
            'total_scheduled': user_posts.filter(status='scheduled').count(),
            'total_posted': user_posts.filter(status='posted').count(),
            'total_failed': user_posts.filter(status='failed').count(),
            'total_cancelled': user_posts.filter(status='cancelled').count(),
            'upcoming_posts': user_posts.filter(
                status='scheduled',
                scheduled_time__gte=timezone.now()
            ).count(),
        }
        
        # Posts by platform
        posts_by_platform = user_posts.values('platform').annotate(
            count=Count('id')
        )
        stats['posts_by_platform'] = {
            item['platform']: item['count']
            for item in posts_by_platform
        }
        
        # Average engagement rate
        avg_engagement = PostAnalytics.objects.filter(
            scheduled_post__user=request.user
        ).aggregate(Avg('engagement_rate'))['engagement_rate__avg']
        
        stats['average_engagement_rate'] = round(avg_engagement, 2) if avg_engagement else 0
        
        serializer = SchedulerStatisticsSerializer(stats)
        return Response(serializer.data)
