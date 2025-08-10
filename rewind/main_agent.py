from agents import (
    Agent,
    function_tool,
    Runner,
    WebSearchTool,
)
import asyncio

from visual_search_agent import agent

description = """
This image shows a stunning coastal view of a Mediterranean city, likely Nice on the French Riviera. The scene features:

A wide, curving bay with striking turquoise and deep blue waters transitioning beautifully from the shoreline outward.

A long pebble beach with scattered people relaxing, sunbathing, and strolling near the surf.

Palm-lined promenades running parallel to the shore, adding a tropical feel.

A wide coastal road with smooth curves following the bay, flanked by pedestrian and cycling lanes.

A cityscape in the background, with mid-rise buildings painted in warm tones (yellows, reds, and creams), stretching up into the hills.

Clear blue skies that suggest warm, sunny weather.

It’s a postcard-perfect scene capturing both the relaxing beach atmosphere and the vibrant urban energy of the French Riviera."""


main_agent = Agent(
    name="Historical agent",
    instructions="""You are a historian. You are given the description of an image, a location and a time period.
    You must reflect on what the scenary would look like at the period.
    Be as historical accurate as possible about the items present in the image. Use the tools provided to search for images and look up information on internet.
    
    For the visual description of the item, you can use the tools you are provided as well.
    """,
    model="o4-mini-2025-04-16",
    tools=[WebSearchTool()],
    handoffs=[agent],
)

async def main():
    # result = await Runner.run(agent, "women dressing in the 16th century in south of France")
    result = await Runner.run(main_agent, f"description:{description}\nlocation: Nice, France\ntime period: 2h century")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
