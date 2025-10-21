"""
Celery configuration for the project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'process-scheduled-posts': {
        'task': 'apps.scheduler.tasks.process_scheduled_posts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-images': {
        'task': 'apps.images.tasks.cleanup_old_images',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
