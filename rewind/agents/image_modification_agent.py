from typing import Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests

class ImageModificationAgent:
    """Agent responsible for modifying images using OpenAI's image generation capabilities."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def modify_image(self, original_image: Image.Image, prompt: str) -> Image.Image:
        """
        Modify the input image using GPT-Image-1 model.
        """
        temp_path = "temp_image.jpg"
        try:
            print(f"Starting image modification with prompt: {prompt}")
            # Save the original image as JPEG
            original_image.save(temp_path, format="JPEG")
            
            print("Sending request to OpenAI...")
            # Open and send the file directly as shown in the documentation
            with open(temp_path, "rb") as img_file:
                response = self.client.images.edit(
                    model="gpt-image-1",
                    image=[img_file],  # Pass as a list with single file object
                    prompt=prompt,
                    n=1,
                    quality="high",
                    size="1024x1536"
                )
                print("Response received from OpenAI")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            # The response directly contains the image data
            if response and response.data and len(response.data) > 0:
                # Get the first generated image
                generated_image = response.data[0]
                
                if hasattr(generated_image, 'b64_json'):
                    # If we got base64 data
                    import base64
                    image_data = base64.b64decode(generated_image.b64_json)
                    return Image.open(BytesIO(image_data))
                elif hasattr(generated_image, 'url'):
                    # If we got a URL
                    img_response = requests.get(generated_image.url)
                    if img_response.status_code == 200:
                        return Image.open(BytesIO(img_response.content))
                    else:
                        print(f"Failed to download image: {img_response.status_code}")
                        return original_image
            
            print("No valid image data in response")
            return original_image
            
        except Exception as e:
            print(f"Detailed error in modify_image: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise ValueError(f"Error modifying image: {e}")