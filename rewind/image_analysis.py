"""Image analysis and location detection."""

from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import cv2
import numpy as np
from typing import Optional

from .config import Config


class ImageAnalyzer:
    """Handles image analysis and location detection."""
    
    def __init__(self):
        self.config = Config()
        self.processor = None
        self.model = None
        self._load_models()
    
    def _load_models(self):
        """Load the image analysis models."""
        try:
            self.processor = BlipProcessor.from_pretrained(
                self.config.image_analysis_model,
                token=self.config.huggingface_token
            )
            self.model = BlipForConditionalGeneration.from_pretrained(
                self.config.image_analysis_model,
                token=self.config.huggingface_token,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                
        except Exception as e:
            print(f"Warning: Could not load image analysis model: {e}")
    
    async def identify_location(self, image: Image.Image) -> str:
        """Identify location from image."""
        try:
            # Use BLIP for image captioning to identify landmarks/locations
            inputs = self.processor(
                image, 
                text="a photography of", 
                return_tensors="pt"
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            out = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Extract location keywords from caption
            location = self._extract_location_from_caption(caption)
            return location or "Unknown Location"
            
        except Exception as e:
            print(f"Error in location identification: {e}")
            return "Unknown Location"
    
    def _extract_location_from_caption(self, caption: str) -> Optional[str]:
        """Extract location information from image caption."""
        # Simple keyword extraction - can be improved
        location_keywords = [
            "tower", "bridge", "building", "cathedral", "church", "palace",
            "statue", "monument", "castle", "museum", "square", "park"
        ]
        
        caption_lower = caption.lower()
        for keyword in location_keywords:
            if keyword in caption_lower:
                # Return the caption as potential location
                return caption.replace("a photography of", "").strip()
        
        return None
