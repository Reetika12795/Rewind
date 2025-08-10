from typing import Dict
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

class ImagePromptAgent:
    """Agent responsible for generating image editing prompts based on historical art context."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def _encode_image(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def analyze_image(self, image: Image.Image) -> str:
        """Analyze the image content using GPT-4."""
        base64_image = self._encode_image(image)
        
        try:
            response = self.client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text", 
                                "text": "Analyze this image in detail. Describe its key visual elements, composition, colors, and main subjects. Be specific but concise."
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ]
            )
            
            # Extract the text response from the output
            for output in response.output:
                if hasattr(output, 'content'):
                    return output.content
            
            print("No text content found in response")
            return ""
            
        except Exception as e:
            print(f"Error in image analysis: {str(e)}")
            raise ValueError(f"Failed to analyze image: {e}")
    
    def generate_image_prompt(self, art_context: Dict[str, str], input_image: Image.Image) -> str:
        """Generate an image editing prompt based on historical art context and input image."""
        try:
            # First, analyze the image
            image_analysis = self.analyze_image(input_image)
            print(f"Image Analysis: {image_analysis}")
            
            # Create a system prompt that uses both the analysis and art context
            system_prompt = """You are an art transformation expert. Create a specific transformation prompt 
            that will modify the analyzed image according to the historical art context. Focus on style, 
            techniques, and visual elements typical of the period."""
            
            user_prompt = f"""Image Analysis: {image_analysis}

Historical Context: {art_context['art_context']}
Location/Year: {art_context['location']}, {art_context['year']}

Generate a precise transformation prompt that will convert the analyzed image into the historical style while 
preserving its core elements. Start with "Transform this image..."."""
            
            # Get the transformation prompt
            response = self.client.chat.completions.create(
                model="o4-mini-2025-04-16",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                #max_completion_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating prompt: {str(e)}")
            raise ValueError(f"Error generating prompt: {e}")
