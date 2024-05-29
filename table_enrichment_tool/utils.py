import re
import json
import textwrap
from IPython.display import Markdown

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