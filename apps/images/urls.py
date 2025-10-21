from django.urls import path
from .views import (
    GenerateImageView,
    ImageListView,
    ImageDetailView,
    ValidateImageView,
    ImageStatisticsView,
    ImageTagListView,
    ImageHistoryView
)

app_name = 'images'

urlpatterns = [
    # Image generation
    path('generate/', GenerateImageView.as_view(), name='generate'),
    
    # Image management
    path('', ImageListView.as_view(), name='list'),
    path('<int:pk>/', ImageDetailView.as_view(), name='detail'),
    path('<int:pk>/validate/', ValidateImageView.as_view(), name='validate'),
    
    # Statistics and history
    path('statistics/', ImageStatisticsView.as_view(), name='statistics'),
    path('history/', ImageHistoryView.as_view(), name='history'),
    
    # Tags
    path('tags/', ImageTagListView.as_view(), name='tags'),
]
