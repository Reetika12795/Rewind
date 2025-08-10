
"""Main application with focus on comprehensive analysis."""

import gradio as gr
from PIL import Image
import asyncio
import json
from typing import Tuple, Optional

from .agents import RewindAnalysisAgent
from .ip_adapter_prompt import IPAdapterPromptBuilder
from .config import Config


class RewindApp:
    """Main application class for Rewind analysis."""
    
    def __init__(self):
        self.config = Config()
        self.analysis_agent = RewindAnalysisAgent()
    # Builder that assembles final IP Adapter friendly prompt payload
        self.prompt_builder = IPAdapterPromptBuilder()
    
    async def analyze_image_comprehensive(
        self, 
        image: Image.Image, 
        location: str,
        target_year: int
    ) -> Tuple[str, str, str, str, str]:
        """Comprehensive analysis pipeline returning formatted results."""
        try:
            # Step 1: Image Analysis
            analysis = await self.analysis_agent.analyze_image(image, location, target_year)
            
            # Step 2: Historical Context
            historical_context = await self.analysis_agent.get_historical_context(
                location, target_year, analysis
            )
            
            # Step 3: Generate Prompt Components
            prompt_components = await self.analysis_agent.generate_prompt_components(
                analysis, historical_context, location, target_year
            )
            payload = self.prompt_builder.build(prompt_components)
            
            # Format outputs
            analysis_output = self._format_analysis_output(analysis)
            context_output = self._format_context_output(historical_context)
            prompts_output = self._format_prompts_output(prompt_components)
            questions_output = self._format_questions_output(analysis, historical_context)
            
            payload_json = json.dumps(payload.to_json(), indent=2)
            return analysis_output, context_output, prompts_output, questions_output, payload_json
            
        except Exception as e:
            error_msg = f"❌ **Error**: {str(e)}"
            return error_msg, error_msg, error_msg, error_msg, error_msg
    
    def _format_analysis_output(self, analysis) -> str:
        """Format image analysis results."""
        output = "# 🔍 Image Analysis Results\n\n"
        
        output += f"## 🏛️ Scene Overview\n"
        output += f"- **Type**: {analysis.scene_type}\n"
        output += f"- **Lighting**: {analysis.lighting_conditions}\n"
        output += f"- **Weather**: {analysis.weather_atmosphere}\n"
        output += f"- **Time**: {analysis.time_of_day}\n"
        output += f"- **Season**: {analysis.season}\n\n"
        
        if analysis.architectural_elements:
            output += f"## 🏗️ Architecture & Buildings\n"
            for element in analysis.architectural_elements:
                output += f"- {element}\n"
            output += "\n"
        
        if analysis.vehicles_transportation:
            output += f"## 🚗 Transportation Visible\n"
            for vehicle in analysis.vehicles_transportation:
                output += f"- {vehicle}\n"
            output += "\n"
        
        if analysis.technology_visible:
            output += f"## 💻 Modern Technology Detected\n"
            for tech in analysis.technology_visible:
                output += f"- {tech}\n"
            output += "\n"
        
        if analysis.clothing_fashion:
            output += f"## 👕 Clothing & Fashion\n"
            for item in analysis.clothing_fashion:
                output += f"- {item}\n"
            output += "\n"
        
        return output
    
    def _format_context_output(self, context) -> str:
        """Format historical context results."""
        output = "# 📚 Historical Context\n\n"
        
        if context.architectural_styles:
            output += f"## 🏛️ Period Architecture\n"
            for style in context.architectural_styles:
                output += f"- {style}\n"
            output += "\n"
        
        if context.common_materials:
            output += f"## 🧱 Construction Materials\n"
            for material in context.common_materials:
                output += f"- {material}\n"
            output += "\n"
        
        if context.transportation_methods:
            output += f"## 🐎 Transportation Methods\n"
            for transport in context.transportation_methods:
                output += f"- {transport}\n"
            output += "\n"
        
        if context.typical_clothing:
            output += f"## 👗 Period Fashion\n"
            for clothing in context.typical_clothing:
                output += f"- {clothing}\n"
            output += "\n"
        
        if context.technology_level:
            output += f"## ⚙️ Technology Level\n"
            for tech in context.technology_level:
                output += f"- {tech}\n"
            output += "\n"
        
        if context.notable_events:
            output += f"## 📅 Notable Events\n"
            for event in context.notable_events[:3]:  # Top 3
                output += f"- {event}\n"
            output += "\n"
        
        return output
    
    def _format_prompts_output(self, prompts) -> str:
        """Format prompt components for IP adapter."""
        output = "# 🎨 IP Adapter Prompt Components\n\n"
        
        output += f"## 🎯 Core Description\n"
        output += f"```\n{prompts.core_description}\n```\n\n"
        
        if prompts.historical_style_tags:
            output += f"## 🏷️ Style Tags\n"
            output += f"```\n{', '.join(prompts.historical_style_tags)}\n```\n\n"
        
        if prompts.architectural_details:
            output += f"## 🏗️ Architectural Details\n"
            for detail in prompts.architectural_details:
                output += f"- {detail}\n"
            output += "\n"
        
        if prompts.atmospheric_elements:
            output += f"## 🌤️ Atmosphere\n"
            for element in prompts.atmospheric_elements:
                output += f"- {element}\n"
            output += "\n"
        
        if prompts.negative_prompts:
            output += f"## ❌ Negative Prompts\n"
            output += f"```\n{', '.join(prompts.negative_prompts)}\n```\n\n"
        
        if prompts.style_modifiers:
            output += f"## 🎨 Style Modifiers\n"
            output += f"```\n{', '.join(prompts.style_modifiers)}\n```\n\n"
        
        # Final combined prompt
        final_prompt = prompts.core_description
        if prompts.historical_style_tags:
            final_prompt += ", " + ", ".join(prompts.historical_style_tags)
        if prompts.style_modifiers:
            final_prompt += ", " + ", ".join(prompts.style_modifiers)
        
        output += f"## 🔥 **Final Combined Prompt**\n"
        output += f"```\n{final_prompt}\n```\n\n"
        
        return output
    
    def _format_questions_output(self, analysis, context) -> str:
        """Format research questions and suggestions."""
        output = "# ❓ Research Questions & Suggestions\n\n"
        
        if analysis.clarification_questions:
            output += f"## 🤔 Clarification Needed\n"
            for question in analysis.clarification_questions:
                output += f"- {question}\n"
            output += "\n"
        
        if analysis.research_suggestions:
            output += f"## 📖 Research Suggestions\n"
            for suggestion in analysis.research_suggestions:
                output += f"- {suggestion}\n"
            output += "\n"
        
        output += f"## 🎯 Key Areas to Research\n"
        if analysis.architectural_style_research:
            output += f"### Architecture:\n"
            for item in analysis.architectural_style_research:
                output += f"- {item}\n"
        
        if analysis.fashion_period_research:
            output += f"### Fashion:\n"
            for item in analysis.fashion_period_research:
                output += f"- {item}\n"
        
        if analysis.cultural_context_needed:
            output += f"### Culture:\n"
            for item in analysis.cultural_context_needed:
                output += f"- {item}\n"
        
        output += f"\n## 💡 **Next Steps**\n"
        output += f"1. Use the **Final Combined Prompt** for your IP adapter\n"
        output += f"2. Research the specific questions listed above\n"
        output += f"3. Adjust the negative prompts based on unwanted modern elements\n"
        output += f"4. Consider the atmospheric elements for better mood matching\n"
        
        return output
    
    def create_interface(self) -> gr.Interface:
        """Create the Gradio interface."""
        def sync_analyze(image, location, year):
            """Synchronous wrapper for async analysis."""
            if not location or not str(location).strip():
                error = "❌ Please provide a location"
                return error, error, error, error, error
            try:
                return asyncio.run(
                    self.analyze_image_comprehensive(image, str(location).strip(), int(year))
                )
            except Exception as e:
                err = f"❌ Error: {e}"
                return err, err, err, err, err
        
        interface = gr.Interface(
            fn=sync_analyze,
            inputs=[
                gr.Image(type="pil", label="📸 Upload Photo"),
                gr.Textbox(
                    placeholder="e.g., Paris, London, New York, Times Square...",
                    label="📍 Location",
                    info="Be as specific as possible for better results"
                ),
                gr.Slider(
                    minimum=1000, 
                    maximum=2000, 
                    value=1850, 
                    step=10,
                    label="🕰️ Target Year",
                    info="What year should this place look like?"
                )
            ],
            outputs=[
                gr.Markdown(label="🔍 Image Analysis"),
                gr.Markdown(label="📚 Historical Context"), 
                gr.Markdown(label="🎨 IP Adapter Prompts"),
                gr.Markdown(label="❓ Research Questions"),
                gr.Code(label="🧩 IP Adapter JSON Payload", language="json")
            ],
            title="⏪ Rewind - Historical Image Analysis",
            description="""
            **Upload a photo and get comprehensive analysis for historical transformation!**
            
            This tool analyzes your image and provides:
            - 🔍 Detailed visual analysis of modern elements
            - 📚 Historical context for your target time period  
            - 🎨 Ready-to-use prompts for IP adapter image generation
            - ❓ Research questions to improve your results
            
            Perfect for preparing images for historical AI transformation!
            """,
            theme=gr.themes.Soft(),
            examples=[
                ["assets/images/street.jpg", "London", 1890],
                ["assets/images/building.jpg", "Paris", 1920],
                ["assets/images/square.jpg", "New York", 1850]
            ],
            allow_flagging="never"
        )
        
        return interface


def create_app() -> gr.Interface:
    """Factory function to create the application."""
    app = RewindApp()
    return app.create_interface()


def main():
    """Main entry point."""
    interface = create_app()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )


if __name__ == "__main__":
    main()