# from agents import Agent, ModelSettings, function_tool

from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
openai_client = OpenAI()

def describe_all_images(images_results):
    descriptions = []
    for image in images_results:
        description = describe_thumbnail(image["thumbnail"])
        descriptions.append({
            "title": image["title"],
            "link": image["link"],
            "description": description
        })
        break
    return descriptions

def describe_thumbnail(image_url):
    response = openai_client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "what's in this image? To what era/year does it belong?"},
                {
                    "type": "input_image",
                    "image_url": image_url,
                },
            ],
        }],
    )
    return response.output_text + "\n"


def search_google(item_to_find: str):
    params = {
    "engine": "google_images_light",
    "q": item_to_find,
    "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    raw_results = search.get_dict()["images_results"]
    images_results = [
        {
            "thumbnail": result["thumbnail"],
            "link": result["link"],
            "title": result["title"]
        }
        for result in raw_results
    ]
    return raw_results 


import requests

def wikipedia_lookup(query):
    # Step 1: Search
    search_url = "https://en.wikipedia.org/w/rest.php/v1/search/title"
    params = {"q": query, "limit": 1}
    search_resp = requests.get(search_url, params=params)
    search_resp.raise_for_status()
    search_data = search_resp.json()
    
    if not search_data.get("pages"):
        return f"No Wikipedia page found for '{query}'"
    
    page_key = search_data["pages"][0]["key"]
    
    # Step 2: Fetch summary
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_key}"
    summary_resp = requests.get(summary_url)
    summary_resp.raise_for_status()
    return summary_resp.json().get("extract")

# Example: LLM decides query should be "United States Constitution"
print(wikipedia_lookup("jeans"))
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


# if __name__ == "__main__":
#     item_to_find = "mediterranean houses in the 16h century"
#     results = search_google(item_to_find)
#     desc = describe_all_images(results)
#     print(desc[0])