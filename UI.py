import gradio as gr
from PIL import Image
from rewind.agents.wikipedia_agent import WikipediaResearchAgent
from rewind.agents.image_prompt_agent import ImagePromptAgent
from rewind.agents.image_modification_agent import ImageModificationAgent


def __init__():
    """
    Initialize the Gradio interface for the Rewind project.
    This function sets up the UI components and their interactions.
    """
    # Initialize agents
    global wiki_agent, prompt_agent, modification_agent
    wiki_agent = WikipediaResearchAgent()
    prompt_agent = ImagePromptAgent()
    modification_agent = ImageModificationAgent()
    print("Agents initialized successfully.")
    global image_input, location_input, year_input
    image_input = None
    location_input = ""
    year_input = ""
    print("Global variables initialized.")

# Define the function that will be called when the "Generate" button is clicked.
# This function takes the user's inputs and returns the output.
# For this example, it simply returns the uploaded image.
def generate_image(input_image, location, year):
    """
    Processes the inputs and generates an output image.
    
    Args:
        input_image (PIL.Image.Image): The image uploaded by the user.
        location (str): The location string entered by the user.
        year (str): The year string entered by the user.
        
    Returns:
        PIL.Image.Image: The processed image to be displayed as output.
    """
    try:
        print(f"Starting image generation for {location}, {year}")
        
        # Get historical art context
        art_context = wiki_agent.research_art_context(int(year), location)
        print(f"Art context retrieved: {art_context}")

        # Generate image editing prompt
        editing_prompt = prompt_agent.generate_image_prompt(art_context, input_image)
        print(f"Generated Editing Prompt: {editing_prompt}")

        # Modify the image using DALL-E
        modified_image = modification_agent.modify_image(input_image, editing_prompt)
        
        # Verify we got a different image back
        if modified_image is not None and isinstance(modified_image, Image.Image):
            print(f"Modified image size: {modified_image.size}")
            print(f"Original image size: {input_image.size}")
            return modified_image
        else:
            print("Warning: No valid modified image returned")
            return input_image
            
    except Exception as e:
        print(f"Error during image generation: {e}")
        import traceback
        print(traceback.format_exc())
        return input_image

# Use gr.Blocks() for more control over the layout of the components.
with gr.Blocks() as demo:
    gr.Markdown("# Rewind Project")
    gr.Markdown("Upload an image, enter a location and year, then click Generate.")
    
    with gr.Row():
        # Left side for inputs
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="Drag & Drop Image Here")
            location_input = gr.Textbox(label="Insert a location")
            year_input = gr.Textbox(label="Insert a year")
            generate_btn = gr.Button("Generate")
            
        # Right side for the output tab
        with gr.Column(scale=1):
            with gr.Tab("Output Result"):
                image_output = gr.Image(label="Generated Image")

    # Define the action for the "Generate" button click.
    # It will call the 'generate_image' function with the values from the input components
    # and display the returned value in the output component.
    generate_btn.click(
        fn=generate_image,
        inputs=[image_input, location_input, year_input],
        outputs=image_output
    )

# Launch the Gradio interface.
if __name__ == "__main__":
    __init__()  # Initialize the agents
    demo.launch()
    print("Gradio interface launched. Visit the provided URL to interact with the app.")
