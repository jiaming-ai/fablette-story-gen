import google.generativeai as genai
import os
from dotenv import load_dotenv
from time import sleep, time
from tqdm import tqdm
import requests
from langfuse.client import Langfuse
from langfuse.decorators import observe, langfuse_context

# Load environment variables from .env file
load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Rate limiting variables
MAX_REQUESTS_PER_MINUTE = 8
request_timestamps = []
model_name = "gemini-2.0-flash-thinking-exp-01-21"
def check_rate_limit():
    """
    Checks if we've exceeded our rate limit and waits if necessary.
    Maintains a rolling window of requests over the last minute.
    """
    current_time = time()
    # Remove timestamps older than 1 minute
    while request_timestamps and current_time - request_timestamps[0] >= 60:
        request_timestamps.pop(0)
    
    if len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - request_timestamps[0])
        if wait_time > 0:
            print(f"\nApproaching rate limit. Waiting {int(wait_time)} seconds...")
            for _ in tqdm(range(int(wait_time)), desc="Waiting"):
                sleep(1)
            request_timestamps.clear()

@observe(as_type="generation")
def call_gemini(system_prompt, user_message, max_retries=3):
    """
    Calls the Gemini language model with a system prompt and user message.

    Argslangfuse_context:
        system_prompt: The system prompt to guide the model's behavior.
        user_message: The user's message to the model.
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        The model's response as a string, or None if there's an error.
    """
    for attempt in range(max_retries):
        try:
            # Check and handle rate limiting
            check_rate_limit()
            
            # Configure API key - Ensure your API key is set as an environment variable
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            if not GOOGLE_API_KEY:
                raise EnvironmentError("Please set the GOOGLE_API_KEY environment variable.")
            genai.configure(api_key=GOOGLE_API_KEY)
            genai.configure(transport='rest')

            model = genai.GenerativeModel(model_name)
            prompt_parts = [system_prompt, user_message]
            response = model.generate_content(prompt_parts)
            
            # Record this request's timestamp
            request_timestamps.append(time())
            
            langfuse_context.update_current_observation(
            input=prompt_parts,
            model=model_name,
            usage_details={
                "input": response.usage_metadata.prompt_token_count,
                "output": response.usage_metadata.candidates_token_count,
                "total": response.usage_metadata.total_token_count
            }
        )
            return response.text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                print(f"\nRate limit hit. Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                for _ in tqdm(range(60), desc="Waiting"):
                    sleep(1)
                continue
            print(f"An error occurred: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

if __name__ == "__main__":
    # Test case
    system_prompt = "You are a helpful and concise assistant."
    user_message = "What is the capital of Singapore?"

    gemini_response = call_gemini(system_prompt, user_message)

    if gemini_response:
        print("System Prompt:", system_prompt)
        print("User Message:", user_message)
        print("Gemini Response:", gemini_response)
    else:
        print("Failed to get response from Gemini.")