import os
import time
import logging
from google.generativeai import configure, list_models
from .utils import create_json_blueprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_gemini_api():
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        e = "API key not found. Please set the GOOGLE_API_KEY environment variable."
        logger.error(e)
        raise ValueError(e)
    
    configure(api_key=api_key)


def available_models():
    configure_gemini_api()
    models = []
    for m in list_models():
        if 'generateContent' in m.supported_generation_methods:
            models.append(m.name)
    return models


def build_prompt(fields_dict, row_data, external_data):
    """
    Build the prompt for the API call.

    Parameters:
        fields_dict (dict): Dictionary of fields and their descriptions.
        row_data (pd.Series): DataFrame row data excluding fields to be updated.
        external_data (dict): Additional external data required for generating the prompt.

    Returns:
        str: The generated prompt.
    """
    prompt = f"""
    **Task:**
    Using the data provided below, generate the following fields for a row in a table, outputted as a JSON:
    {fields_dict}

    **Existing Row Data**
    {row_data.to_dict()}

    **External Data**
    {external_data}

    **Example Output (Success):**
    ```json
    {create_json_blueprint(list(fields_dict.keys()))}
    ```
    """
    return prompt


def call_gemini(model, prompt, max_retries=5, retry_delay=60):
    """
    Calls a generative model to produce content based on a given prompt.

    This function sends a prompt to a pre-defined model and retrieves the generated content,
    typically used for generating text based on input parameters.

    Parameters:
        model (GenerativeModel): The model object capable of generating content.
        prompt (str): A string prompt that describes what content the model should generate.

    Returns:
        response: The response from the model containing the generated content. The type of this
                  response can vary depending on the implementation of the model's generate_content method.
    """
    try:
        configure_gemini_api()
    except ValueError as e:
        logger.error("Gemini API is not configured. Exiting call_gemini.")
        raise

    for attempt in range(max_retries):
        try:
            logger.info("Calling Gemini...")
            response = model.generate_content([prompt])
            return response
        except Exception as e:
            logger.error(f"Error: {e}, Attempt: {attempt + 1}")
            time.sleep(retry_delay)
    
    raise Exception("API request failed after maximum retries")