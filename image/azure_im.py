import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests
from PIL import Image
import json

# Load environment variables from .env file
load_dotenv()

client = AzureOpenAI(
    api_version="2024-02-01",  
    api_key=os.environ["AZURE_API_KEY"],  
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
)

def generate_and_save_image(prompt, filename):
    """
    Generate an image using DALL-E 3 and save it to the specified filename.
    
    Args:
        prompt (str): The description of the image to generate
        filename (str): The name of the file to save the image (without path)
    
    Returns:
        str: The full path to the saved image
    """
    # Initialize Azure OpenAI client

    # Generate the image
    result = client.images.generate(
        model="Dalle3",
        prompt=prompt,
        style="natural", # vivid, natural
        size="1024x1024", # 1792x1024, 1024x1792, 1024x1024
        n=1
    )

    json_response = json.loads(result.model_dump_json())

    # Set the directory for the stored image
    image_dir = "data/images"

    # If the directory doesn't exist, create it
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Ensure filename ends with .png
    if not filename.endswith('.png'):
        filename = f"{filename}.png"

    # Create the full image path
    image_path = os.path.join(image_dir, filename)

    # Retrieve and save the generated image
    image_url = json_response["data"][0]["url"]
    generated_image = requests.get(image_url).content
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)

    return image_path

# Example usage:
if __name__ == "__main__":
    prompt = "Pastel art illustration for a children's book cover. A kind-looking Mother Hulda with a young girl, Lily, in a cozy cottage window high in the clouds. Feathers are playfully floating out of the window, turning into snowflakes as they drift downwards towards a green forest below. Gentle, bright colors, whimsical atmosphere."
    saved_image_path = generate_and_save_image(prompt, "mother_hulda")
    
    # # Optionally display the image
    # image = Image.open(saved_image_path)
    # image.show()