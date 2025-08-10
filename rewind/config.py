"""Configuration management for Rewind."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    
    # OpenAI Model configurations
    # Updated default models (old gpt-4-vision-preview deprecated)
    vision_model: str = os.getenv("REWIND_VISION_MODEL", "gpt-4o-mini")
    text_model: str = os.getenv("REWIND_TEXT_MODEL", "gpt-4o")
    
    # Analysis parameters
    max_analysis_tokens: int = 2000
    max_context_tokens: int = 1500
    max_prompt_tokens: int = 1200
    temperature: float = 0.3
    # Feature flags
    enable_wiki: bool = False
    prompt_only: bool = False
    
    # File paths
    base_dir: Path = Path(__file__).parent.parent
    assets_dir: Path = base_dir / "assets"
    
    # Image processing
    max_image_size: int = 1024  # Max dimension for processing
    
    def __post_init__(self):
        """Load environment variables."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.enable_wiki = os.getenv("REWIND_ENABLE_WIKI", "1") not in ("0", "false", "False")
        self.prompt_only = os.getenv("PROMPT_ONLY", "0") in ("1", "true", "True")

        if not self.openai_api_key and not self.prompt_only:
            raise ValueError("OPENAI_API_KEY environment variable is required (or set PROMPT_ONLY=1)")
        
        # Create directories if they don't exist
        self.assets_dir.mkdir(parents=True, exist_ok=True)