import gradio as gr
from PIL import Image

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
    # In a real application, you would add your image processing logic here.
    # For demonstration, we'll just display the original image.
    print(f"Location: {location}, Year: {year}")
    
    if input_image is None:
        # Create a blank image if no input is provided to avoid errors.
        return Image.new('RGB', (512, 512), color = 'lightgray')
        
    return input_image

# Use gr.Blocks() for more control over the layout of the components.
with gr.Blocks() as demo:
    gr.Markdown("# Image Generation Project")
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
    demo.launch()
    print("Gradio interface launched. Visit the provided URL to interact with the app.")
