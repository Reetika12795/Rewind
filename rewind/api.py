"""FastAPI endpoints for Rewind analysis system."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from typing import Dict, Any

from .agents import RewindAnalysisAgent, AnalysisResult, HistoricalContext, PromptComponents


app = FastAPI(
    title="Rewind Analysis API",
    description="AI-powered historical image analysis for time travel photography",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the analysis agent
analysis_agent = RewindAnalysisAgent()


@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    location: str = Form(...),
    target_year: int = Form(...)
):
    """
    Comprehensive image analysis endpoint.
    
    Returns:
    - Image analysis results
    - Historical context
    - IP adapter prompt components
    - Research suggestions
    """
    try:
        # Validate inputs
        if target_year < 1000 or target_year > 2000:
            raise HTTPException(status_code=400, detail="Target year must be between 1000 and 2000")
        
        if not location.strip():
            raise HTTPException(status_code=400, detail="Location is required")
        
        # Process the uploaded image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Run the analysis pipeline
        analysis = await analysis_agent.analyze_image(pil_image, location, target_year)
        historical_context = await analysis_agent.get_historical_context(location, target_year, analysis)
        prompt_components = await analysis_agent.generate_prompt_components(
            analysis, historical_context, location, target_year
        )
        
        # Format the response
        return {
            "success": True,
            "input": {
                "location": location,
                "target_year": target_year,
                "image_info": {
                    "size": pil_image.size,
                    "mode": pil_image.mode
                }
            },
            "analysis": analysis.dict(),
            "historical_context": historical_context.dict(),
            "prompt_components": prompt_components.dict(),
            "next_steps": {
                "ip_adapter_prompt": prompt_components.core_description + " " + " ".join(prompt_components.historical_style_tags),
                "negative_prompt": " ".join(prompt_components.negative_prompts),
                "style_modifiers": prompt_components.style_modifiers,
                "research_needed": analysis.research_suggestions
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/quick-analysis", response_model=AnalysisResult)
async def quick_analysis_endpoint(
    image: UploadFile = File(...),
    location: str = Form(...),
    target_year: int = Form(...)
):
    """Quick image analysis only - for faster iterations."""
    try:
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        analysis = await analysis_agent.analyze_image(pil_image, location, target_year)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rewind-analysis"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)