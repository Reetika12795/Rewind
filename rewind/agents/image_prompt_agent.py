from typing import Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import base64
from io import BytesIO

class ImagePromptAgent:
    """Agent responsible for generating image editing prompts based on historical art context."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def preprocess_image(self, input_image: Image.Image) -> str:
        """Preprocess image to reduce token consumption."""
        # Resize image to smaller dimensions
        max_size = (512, 512)
        input_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compress image with reduced quality
        buffered = BytesIO()
        input_image.save(buffered, format="JPEG", quality=50, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode()

    def generate_image_prompt(self, art_context: Dict[str, str], input_image: Image.Image) -> str:
        """
        Generate an image editing prompt based on historical art context and input image.
        
        Args:
            art_context: Dictionary containing historical art context from WikipediaResearchAgent
            input_image: PIL Image object to be analyzed and edited
            
        Returns:
            String containing the generated image editing prompt
        
        Raises:
            ValueError: If input_image is None or invalid
        """
        if input_image is None:
            raise ValueError("Input image cannot be None")
        
        try:
            # Use preprocessed image
            img_str = self.preprocess_image(input_image)

            system_prompt = """You are an image analysis expert. First analyze the provided base64 image, then create a transformation prompt.
            1. Describe key elements in the original image (composition, colors, subjects)
            2. Suggest specific style transformations based on the historical context
            Keep final prompt under 60 words."""
            
            user_prompt = f"""Step 1 - Analyze this image: {img_str}
            
            Step 2 - Based on the analysis above, create a transformation prompt using:
            - Historical Context: {art_context['art_context']}
            - Location/Year: {art_context['location']}, {art_context['year']}
            
            Keep the core elements of the original image while applying period-appropriate style."""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",  # More reliable for image analysis
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=120  # Reduced tokens for more focused response
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"Error processing image: {e}")
