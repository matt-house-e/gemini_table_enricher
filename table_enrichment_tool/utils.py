import re
import json
import textwrap
import logging
import pandas as pd
import fitz  # PyMuPDF
from IPython.display import Markdown

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.CRITICAL

def ensure_columns_exist(df, fields_dict):
    for field in fields_dict.keys():
        if field not in df.columns:
            df[field] = None
    return df


def print_wrapped(text: str, width: int = 80) -> None:
    """Print long text wrapped to the specified width."""
    wrapped_text = textwrap.fill(text, width=width)
    print(wrapped_text)


def convert_list_to_string(value_list):
    return ', '.join(map(str, value_list))


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def create_json_blueprint(fields):
    """
    Create a JSON blueprint from a list of fields.

    Parameters:
        fields (list): A list of field names to be used as keys in the JSON blueprint.

    Returns:
        str: A JSON-formatted string representing the blueprint.
    """
    blueprint_dict = {field: "" for field in fields}
    return json.dumps(blueprint_dict, indent=2)


def extend_search(text, span):
    # Extend the search to try to capture nested structures
    start, end = span
    nest_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            nest_count += 1
        elif text[i] == '}':
            nest_count -= 1
            if nest_count == 0:
                return text[start:i+1]
    return text[start:end]


def extract_json(text_response):
    # This pattern matches a string that starts with '{' and ends with '}'
    pattern = r'\{[^{}]*\}'

    matches = re.finditer(pattern, text_response)
    json_objects = []
    for match in matches:
        json_str = match.group(0)
        try:
            # Validate if the extracted string is valid JSON
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            # Extend the search for nested structures
            extended_json_str = extend_search(text_response, match.span())
            try:
                json_obj = json.loads(extended_json_str)
                json_objects.append(json_obj)
            except json.JSONDecodeError:
                # Handle cases where the extraction is not valid JSON
                continue
    if json_objects:
        return json_objects
    else:
        return None  # Or handle this case as you prefer

def extract_text_from_pdf(file_path):
    """
    Extracts all text from a PDF file.

    Parameters:
        file_path (str): The file path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    try:
        # Open the PDF file
        document = fitz.open(file_path)
        # Initialize text variable
        text = ""
        # Iterate through each page
        for page_num in range(len(document)):
            # Get the page
            page = document.load_page(page_num)
            # Extract text from the page
            text += page.get_text()
        return text
    except Exception as e:
        logging.error(f"Error reading PDF file at {file_path}: {e}")
        return ""


def chunk_text(text, num_chunks):
    """
    Splits text into specified number of chunks.

    Parameters:
        text (str): The text to split.
        num_chunks (int): The number of chunks to split the text into.

    Returns:
        list: A list of text chunks.
    """
    # Split the text into words
    words = text.split()
    # Calculate the approximate number of words per chunk
    chunk_size = len(words) // num_chunks
    # Create the list of chunks
    chunks = [' '.join(words[i * chunk_size: (i + 1) * chunk_size]) for i in range(num_chunks)]
    
    # Handle any remaining words by appending them to the last chunk
    if len(words) % num_chunks != 0:
        chunks[-1] += ' ' + ' '.join(words[num_chunks * chunk_size:])
    
    return chunks


def save_chunks_to_csv(chunks, output_path):
    """
    Saves text chunks to a CSV file, each chunk as a separate row.

    Parameters:
        chunks (list): The list of text chunks.
        output_path (str): The file path to save the CSV file.
    
    Returns:
        None
    """
    # Create a DataFrame from the chunks
    df = pd.DataFrame({'Text Chunk': chunks})
    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)
