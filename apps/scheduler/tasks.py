"""
Celery tasks for scheduling and publishing posts
"""
from celery import shared_task
from django.utils import timezone
from .models import ScheduledPost, PostAnalytics
from .services import PlatformPublisherFactory
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def publish_scheduled_post(self, post_id):
    """
    Celery task to publish a scheduled post
    
    Args:
        post_id (int): ID of the ScheduledPost instance
    """
    try:
        # Get the scheduled post
        post = ScheduledPost.objects.get(id=post_id)
        
        # Check if post is ready to be published
        if not post.is_due:
            logger.warning(f"Post {post_id} is not due yet")
            return {'status': 'not_due', 'post_id': post_id}
        
        if post.status != 'scheduled':
            logger.warning(f"Post {post_id} status is {post.status}, not scheduled")
            return {'status': 'invalid_status', 'post_id': post_id}
        
        # Update status to processing
        post.status = 'processing'
        post.save()
        
        # Get the appropriate publisher for the platform
        publisher = PlatformPublisherFactory.get_publisher(post.platform)
        
        # Publish the post
        result = publisher.publish(post)
        
        if result['success']:
            # Update post status
            post.status = 'posted'
            post.posted_at = timezone.now()
            post.platform_post_id = result.get('platform_post_id', '')
            post.platform_post_url = result.get('platform_post_url', '')
            post.save()
            
            # Create analytics record
            PostAnalytics.objects.create(scheduled_post=post)
            
            logger.info(f"Post {post_id} published successfully to {post.platform}")
            return {
                'status': 'success',
                'post_id': post_id,
                'platform': post.platform,
                'platform_post_url': post.platform_post_url
            }
        else:
            # Publishing failed
            post.status = 'failed'
            post.error_message = result.get('error', 'Unknown error')
            post.save()
            
            logger.error(f"Failed to publish post {post_id}: {result.get('error')}")
            return {
                'status': 'failed',
                'post_id': post_id,
                'error': result.get('error')
            }
            
    except ScheduledPost.DoesNotExist:
        logger.error(f"Post {post_id} not found")
        return {'status': 'error', 'message': 'Post not found'}
        
    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {str(e)}")
        
        # Update post status
        try:
            post = ScheduledPost.objects.get(id=post_id)
            post.status = 'failed'
            post.error_message = str(e)
            post.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@shared_task
def process_scheduled_posts():
    """
    Celery task to process all due scheduled posts
    Runs every 5 minutes via Celery Beat
    """
    try:
        # Get all posts that are due
        due_posts = ScheduledPost.objects.filter(
            status='scheduled',
            scheduled_time__lte=timezone.now()
        )
        
        count = due_posts.count()
        
        if count == 0:
            logger.info("No posts due for publishing")
            return {'status': 'success', 'processed': 0}
        
        # Trigger publishing for each post
        results = []
        for post in due_posts:
            result = publish_scheduled_post.delay(post.id)
            results.append({
                'post_id': post.id,
                'task_id': result.id
            })
        
        logger.info(f"Started publishing {count} posts")
        return {
            'status': 'success',
            'processed': count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error processing scheduled posts: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def sync_post_analytics(post_id):
    """
    Celery task to sync analytics for a published post
    
    Args:
        post_id (int): ID of the ScheduledPost instance
    """
    try:
        post = ScheduledPost.objects.get(id=post_id)
        
        if post.status != 'posted':
            logger.warning(f"Post {post_id} is not published, cannot sync analytics")
            return {'status': 'not_published', 'post_id': post_id}
        
        # Get the publisher
        publisher = PlatformPublisherFactory.get_publisher(post.platform)
        
        # Get analytics
        result = publisher.get_analytics(post.platform_post_id)
        
        if result['success']:
            # Update or create analytics
            analytics, created = PostAnalytics.objects.get_or_create(
                scheduled_post=post
            )
            
            analytics.likes = result.get('likes', 0)
            analytics.comments = result.get('comments', 0)
            analytics.shares = result.get('shares', 0)
            analytics.views = result.get('views', 0)
            analytics.reach = result.get('reach', 0)
            analytics.impressions = result.get('impressions', 0)
            analytics.raw_data = result
            analytics.save()
            
            # Calculate engagement rate
            analytics.calculate_engagement_rate()
            
            logger.info(f"Analytics synced for post {post_id}")
            return {
                'status': 'success',
                'post_id': post_id,
                'analytics': {
                    'likes': analytics.likes,
                    'comments': analytics.comments,
                    'engagement_rate': analytics.engagement_rate
                }
            }
        else:
            logger.error(f"Failed to sync analytics for post {post_id}: {result.get('error')}")
            return {
                'status': 'failed',
                'post_id': post_id,
                'error': result.get('error')
            }
            
    except ScheduledPost.DoesNotExist:
        logger.error(f"Post {post_id} not found")
        return {'status': 'error', 'message': 'Post not found'}
        
    except Exception as e:
        logger.error(f"Error syncing analytics for post {post_id}: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def sync_all_analytics():
    """
    Celery task to sync analytics for all published posts
    Runs daily via Celery Beat
    """
    try:
        # Get all published posts from the last 30 days
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        published_posts = ScheduledPost.objects.filter(
            status='posted',
            posted_at__gte=cutoff_date
        )
        
        count = published_posts.count()
        
        if count == 0:
            logger.info("No posts to sync analytics for")
            return {'status': 'success', 'synced': 0}
        
        # Trigger analytics sync for each post
        results = []
        for post in published_posts:
            result = sync_post_analytics.delay(post.id)
            results.append({
                'post_id': post.id,
                'task_id': result.id
            })
        
        logger.info(f"Started syncing analytics for {count} posts")
        return {
            'status': 'success',
            'synced': count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error syncing all analytics: {str(e)}")
        return {'status': 'error', 'message': str(e)}
