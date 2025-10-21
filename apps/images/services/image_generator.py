"""
Service for generating images using Blackbox AI API
"""
import time
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image as PILImage


class ImageGeneratorService:
    """
    Service class for generating images using Blackbox AI
    """
    
    def __init__(self):
        self.api_key = settings.BLACKBOX_API_KEY
        self.api_url = "https://api.blackbox.ai/v1/image"
    
    def generate_image(self, prompt, negative_prompt="", style="realistic", 
                      width=1024, height=1024, quality="standard"):
        """
        Generate an image using Blackbox AI
        
        Args:
            prompt (str): Description of the image to generate
            negative_prompt (str): Elements to avoid in the image
            style (str): Style of the image
            width (int): Width of the image
            height (int): Height of the image
            quality (str): Quality of the image ('standard' or 'hd')
        
        Returns:
            dict: Dictionary containing image_url and metadata
        """
        try:
            start_time = time.time()
            
            # Prepare the prompt with style
            full_prompt = self._prepare_prompt(prompt, negative_prompt, style)
            
            # Prepare request payload for Blackbox AI
            payload = {
                "prompt": full_prompt,
                "width": width,
                "height": height,
                "steps": 50 if quality == "hd" else 30,
                "guidance_scale": 7.5,
                "negative_prompt": negative_prompt if negative_prompt else None
            }
            
            # Make request to Blackbox AI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            generation_time = time.time() - start_time
            
            # Extract image URL from response
            # Adjust based on actual Blackbox AI response structure
            image_url = result.get('image_url') or result.get('url') or result.get('data', {}).get('url')
            
            if not image_url:
                raise ValueError("No image URL in response")
            
            return {
                'success': True,
                'image_url': image_url,
                'generation_time': generation_time,
                'metadata': {
                    'original_prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'style': style,
                    'width': width,
                    'height': height,
                    'quality': quality,
                    'steps': payload['steps'],
                    'guidance_scale': payload['guidance_scale'],
                    'model': 'blackbox-ai'
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API Request Error: {str(e)}",
                'metadata': {
                    'original_prompt': prompt,
                    'error_type': 'RequestException'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'original_prompt': prompt,
                    'error_type': type(e).__name__
                }
            }
    
    def _prepare_prompt(self, prompt, negative_prompt, style):
        """
        Prepare the full prompt with style
        Blackbox AI supports negative prompts separately
        """
        full_prompt = prompt
        
        # Add style to prompt
        style_descriptions = {
            'realistic': 'photorealistic, high quality, detailed, 8k resolution',
            'artistic': 'artistic, creative, expressive, masterpiece',
            'cartoon': 'cartoon style, animated, colorful, vibrant',
            'abstract': 'abstract art, modern, conceptual, unique',
            'vintage': 'vintage style, retro, classic, nostalgic',
            'minimalist': 'minimalist, simple, clean design, elegant',
            'anime': 'anime style, manga, japanese animation',
            'digital_art': 'digital art, concept art, trending on artstation'
        }
        
        if style in style_descriptions:
            full_prompt = f"{prompt}, {style_descriptions[style]}"
        
        return full_prompt
    
    def download_and_save_image(self, image_url):
        """
        Download image from URL and return as Django file
        
        Args:
            image_url (str): URL of the image to download
        
        Returns:
            ContentFile: Django ContentFile object
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create ContentFile from image data
            image_content = ContentFile(response.content)
            
            return {
                'success': True,
                'file': image_content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_thumbnail(self, image_file, size=(300, 300)):
        """
        Create a thumbnail from an image file
        
        Args:
            image_file: Django ImageField file
            size (tuple): Thumbnail size (width, height)
        
        Returns:
            ContentFile: Thumbnail as ContentFile
        """
        try:
            # Open image
            img = PILImage.open(image_file)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, PILImage.Resampling.LANCZOS)
            
            # Save to BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_io.seek(0)
            
            return ContentFile(thumb_io.read())
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
