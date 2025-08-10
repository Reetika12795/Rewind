from typing import Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from ..wikipedia_scraper import WikipediaScraper

class WikipediaResearchAgent:
    """Agent responsible for researching historical art context from Wikipedia."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.scraper = WikipediaScraper()
        
    def research_art_context(self, year: int, location: str) -> Dict[str, str]:
        """
        Research art context for a specific year and location using Wikipedia data.
        
        Args:
            year: The target year to research
            location: The geographical location to focus on
            
        Returns:
            Dict containing historical art context and relevant information
        """
        # First, get relevant Wikipedia content
        wiki_content = self.scraper.search_art_history(year, location)
        
        # Create a concise prompt for GPT to analyze the content
        system_prompt = f"""You are an art historian expert. Analyze the following information about art 
        in {location} around {year} and extract key details into a 50-word text about:
        1. Art movements active during this time
        2. Notable artists and their work
        3. Cultural context and influences
        4. Architectural and visual arts developments
        
        Provide a short and concise but informative summary."""
        
        # Get GPT's analysis
        response = self.client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": wiki_content}
            ]
        )
        
        analysis = response.choices[0].message.content
        
        print('Analysis:', analysis)
        return {
            "year": str(year),
            "location": location,
            "art_context": analysis,
            "raw_wiki_data": wiki_content
        }
