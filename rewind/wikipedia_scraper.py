import wikipediaapi
from typing import Optional

class WikipediaScraper:
    """Class responsible for scraping art history information from Wikipedia."""
    
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='RewindApp/1.0'
        )
    
    def search_art_history(self, year: int, location: str) -> str:
        """
        Search Wikipedia for art history information about a specific year and location.
        
        Args:
            year: The target year to research
            location: The geographical location to focus on
            
        Returns:
            String containing relevant Wikipedia content 
        """
        # Construct search queries
        queries = [
            f"Art in {location} in {year}",
            f"{location} art {year}s",
            f"{year}s in {location}",
            f"Art movements in {location} {year}s",
            f"Culture of {location} in the {year}s"
        ]
        
        combined_content = []
        
        for query in queries:
            page = self.wiki.page(query)
            if page.exists():
                combined_content.append(page.summary)
        
        if not combined_content:
            # If no specific results found, try broader context
            broader_queries = [
                f"{year}s in art",
                f"Art movements of the {year}s",
                f"{location} art history"
            ]
            
            for query in broader_queries:
                page = self.wiki.page(query)
                if page.exists():
                    combined_content.append(page.summary)
        
        return "\n\n".join(combined_content) if combined_content else f"No information found for art in {location} during {year}."