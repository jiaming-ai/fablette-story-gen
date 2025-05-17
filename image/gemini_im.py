from google.generativeai import GenerativeModel, configure
import os   
from dotenv import load_dotenv
import PIL
import io
from google.generativeai import types

from google import genai

# Load environment variables from .env file
load_dotenv()

# TODO: Replace with your actual API key
configure(api_key=os.getenv("GOOGLE_API_KEY"))

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the Gemini Pro Vision model

# Load the Gemini Pro Vision model

def generate_image(prompt: str, output_filename: str = "generated_image.jpg") -> None:
    """
    Generates an image based on the provided prompt using the Gemini Pro Vision model
    and saves it as a JPG file.

    Args:
        prompt: The text prompt describing the desired image.
        output_filename: The filename to save the generated image as (default: "generated_image.jpg").

    Returns:
        None. Saves the image to a file.
    """
    client = GenerativeModel(model_name="imagen-3.0-generate-002")
    
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="BLOCK_ONLY_HIGH"
        )
    )
    
    # Get the first generated image
    generated_image = response.generated_images[0]
    
    # Save the image to a file
    with open(output_filename, 'wb') as f:
        f.write(generated_image.image.image_bytes)

if __name__ == '__main__':
    # image_prompt = "A futuristic cityscape at sunset"
    # generate_image(image_prompt, "futuristic_city.jpg")

    another_prompt = "A cute cat wearing a hat"
    generate_image(another_prompt, "cute_cat_hat.jpg")
