"""
Celery tasks for image generation and processing
"""
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import GeneratedImage, ImageGenerationHistory
from .services import ImageGeneratorService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_image_task(self, image_id):
    """
    Celery task to generate an image asynchronously
    
    Args:
        image_id (int): ID of the GeneratedImage instance
    """
    try:
        # Get the image instance
        image = GeneratedImage.objects.get(id=image_id)
        
        # Update status to generating
        image.status = 'generating'
        image.save()
        
        # Initialize the image generator service
        generator = ImageGeneratorService()
        
        # Generate the image
        result = generator.generate_image(
            prompt=image.prompt,
            negative_prompt=image.negative_prompt,
            style=image.style,
            width=image.width,
            height=image.height,
            quality=image.quality
        )
        
        if result['success']:
            # Download and save the image
            image.image_url = result['image_url']
            image.metadata = result['metadata']
            image.generation_time = result['generation_time']
            
            # Download the image file
            download_result = generator.download_and_save_image(result['image_url'])
            
            if download_result['success']:
                # Save the image file
                filename = f"generated_{image.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png"
                image.image_file.save(filename, download_result['file'], save=False)
                
                # Create thumbnail
                thumbnail = generator.create_thumbnail(image.image_file)
                if thumbnail:
                    thumb_filename = f"thumb_{image.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    image.thumbnail.save(thumb_filename, thumbnail, save=False)
            
            # Update status to generated
            image.status = 'generated'
            image.save()
            
            # Log the generation
            ImageGenerationHistory.objects.create(
                user=image.user,
                image=image,
                action='generated',
                details={
                    'generation_time': result['generation_time'],
                    'model': result['metadata'].get('model', 'unknown')
                }
            )
            
            logger.info(f"Image {image_id} generated successfully")
            return {'status': 'success', 'image_id': image_id}
            
        else:
            # Generation failed
            image.status = 'failed'
            image.error_message = result.get('error', 'Unknown error')
            image.save()
            
            # Log the failure
            ImageGenerationHistory.objects.create(
                user=image.user,
                image=image,
                action='failed',
                details={'error': result.get('error', 'Unknown error')}
            )
            
            logger.error(f"Image {image_id} generation failed: {result.get('error')}")
            return {'status': 'failed', 'image_id': image_id, 'error': result.get('error')}
            
    except GeneratedImage.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return {'status': 'error', 'message': 'Image not found'}
        
    except Exception as e:
        logger.error(f"Error generating image {image_id}: {str(e)}")
        
        # Update image status
        try:
            image = GeneratedImage.objects.get(id=image_id)
            image.status = 'failed'
            image.error_message = str(e)
            image.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_old_images():
    """
    Celery task to clean up old rejected or failed images
    Runs daily to free up storage space
    """
    from datetime import timedelta
    
    try:
        # Delete images older than 30 days that are rejected or failed
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_images = GeneratedImage.objects.filter(
            status__in=['rejected', 'failed'],
            created_at__lt=cutoff_date
        )
        
        count = old_images.count()
        
        # Delete the images
        for image in old_images:
            # Delete the actual files
            if image.image_file:
                image.image_file.delete(save=False)
            if image.thumbnail:
                image.thumbnail.delete(save=False)
            
            # Delete the database record
            image.delete()
        
        logger.info(f"Cleaned up {count} old images")
        return {'status': 'success', 'deleted_count': count}
        
    except Exception as e:
        logger.error(f"Error cleaning up old images: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def batch_generate_images(image_ids):
    """
    Celery task to generate multiple images in batch
    
    Args:
        image_ids (list): List of GeneratedImage IDs
    """
    results = []
    
    for image_id in image_ids:
        result = generate_image_task.delay(image_id)
        results.append({
            'image_id': image_id,
            'task_id': result.id
        })
    
    return {
        'status': 'success',
        'message': f'Started generation for {len(image_ids)} images',
        'results': results
    }
