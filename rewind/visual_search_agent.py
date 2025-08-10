# from agents import Agent, ModelSettings, function_tool

from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")

def search_google(item_to_find: str):
    params = {
    "engine": "google_images_light",
    "q": item_to_find,
    "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    raw_results = search.get_dict()["images_results"]
    print(raw_results)
    images_results = [
        {
            "thumbnail": result["thumbnail"],
            "link": result["link"],
            "title": result["title"]
        }
        for result in raw_results
    ]
    return raw_results 
    # I actully can use the thumbnail here 

# @function_tool
# def get_weather(city: str) -> str:
#      """returns weather info for the specified city."""
#     return f"The weather in {city} is sunny"

#tool1 get the image 
#tool2 downscale the image and analyze it 
#tool3 wikipedia to get more context about what is expected
#output, between 3 and 5 images that match the query 

# final step: le llm get the matching images and return them to the user
# if not, tell them that it's not possible

# agent = Agent(
#     name="Image reference finder",
#     instructions="You find visual references to what the user is looking for. To do so, you use a visual search model.",
#     model="o3-mini",
#     tools=[get_weather],
# )


if __name__ == "__main__":
    item_to_find = "mediterranean houses in the 16h century"
    results = search_google(item_to_find)
    for result in results:
        print(f"Title: {result['title']}, Link: {result['link']}")