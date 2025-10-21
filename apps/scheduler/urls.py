from django.urls import path
from .views import (
    SchedulePostView,
    ScheduledPostListView,
    ScheduledPostDetailView,
    CancelScheduledPostView,
    PublishNowView,
    PostingScheduleListView,
    PostingScheduleDetailView,
    PostAnalyticsView,
    SyncAnalyticsView,
    SchedulerStatisticsView
)

app_name = 'scheduler'

urlpatterns = [
    # Scheduled posts
    path('schedule/', SchedulePostView.as_view(), name='schedule'),
    path('posts/', ScheduledPostListView.as_view(), name='posts_list'),
    path('posts/<int:pk>/', ScheduledPostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/cancel/', CancelScheduledPostView.as_view(), name='cancel_post'),
    path('posts/<int:pk>/publish-now/', PublishNowView.as_view(), name='publish_now'),
    
    # Posting schedules
    path('schedules/', PostingScheduleListView.as_view(), name='schedules_list'),
    path('schedules/<int:pk>/', PostingScheduleDetailView.as_view(), name='schedule_detail'),
    
    # Analytics
    path('posts/<int:pk>/analytics/', PostAnalyticsView.as_view(), name='post_analytics'),
    path('posts/<int:pk>/sync-analytics/', SyncAnalyticsView.as_view(), name='sync_analytics'),
    
    # Statistics
    path('statistics/', SchedulerStatisticsView.as_view(), name='statistics'),
]
