from openai import AzureOpenAI
from dotenv import load_dotenv
from langfuse.client import Langfuse
import os
# Load environment variables from .env file
load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)
def call_azure_gpt4(prompt: str, system_prompt: str = None) -> str:
    """
    Call Azure OpenAI GPT-4 API with a given prompt and optional system prompt.
    
    Args:
        prompt (str): The input text prompt
        system_prompt (str, optional): System prompt to set context/behavior
        
    Returns:
        str: The model's response text
    """
    
    # Initialize Langfuse client

    # Create a trace
    trace = langfuse.trace(
        name="azureGPT4Generation",
        public=False
    )

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    # Prepare messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        # Create generation span
        generation = trace.generation(
            input=messages,
            model=model
        )

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=3000,
        )
        
        # Extract and return the response text
        if response.choices:
            generated_text = response.choices[0].message.content.strip()
            generation.end(output=generated_text)
            trace.update(output=generated_text)
            langfuse.flush()
            return generated_text

        generation.end(error="No response choices available")
        trace.update(error="No response choices available")
        langfuse.flush()
        return None
        
    except Exception as e:
        error_message = f"Error calling Azure OpenAI API: {str(e)}"
        print(error_message)
        generation.end(error=error_message)
        trace.update(error=error_message)
        langfuse.flush()
        return None

# Example usage
if __name__ == "__main__":
    system_prompt = "You are a helpful assistant that specializes in geography."
    response = call_azure_gpt4("What is the capital of France?", system_prompt)
    if response:
        print(response)