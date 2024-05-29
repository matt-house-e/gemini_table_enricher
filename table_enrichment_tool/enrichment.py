import logging
import textwrap
import pandas as pd
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import extract_json, ensure_columns_exist, convert_list_to_string
from .scraper import get_text_content
from .gemini_api import build_prompt, call_gemini
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def enrich_table(csv_path, output_path, fields_dict, external_data, model_name, url_field_name=False, batch_size=10, max_workers=4):
    """
    Updates a CSV file with new contact information obtained via an API in batches,
    saving after each batch to ensure progress is not lost on failure.

    Parameters:
        csv_path (str): The file path to the source CSV file.
        output_path (str): The file save path for the updated CSV.
        fields_dict (dict): Dictionary of fields and their descriptions for the API.
        external_data (dict): Additional external data required for generating the prompt.
        model_name (str): The model name used for generating new content based on prompts.
        batch_size (int): The number of rows in each processing batch.
        max_workers (int): The maximum number of threads to use for parallel processing.
    """
    # Load CSV data
    df = pd.read_csv(csv_path)

    # Ensure all required columns exist
    df = ensure_columns_exist(df, fields_dict)

    # Process data in batches
    for start in range(0, df.shape[0], batch_size):
        end = start + batch_size
        batch = df[start:end]

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_row, row, fields_dict, external_data, model_name, url_field_name): idx
                for idx, row in batch.iterrows()
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append((idx, result))
                except Exception as e:
                    logging.error(f"Error processing row {idx}: {e}")
                    results.append((idx, pd.Series({field: None for field in fields_dict.keys()})))

        # Update the batch with results
        for idx, result in results:
            if idx not in batch.index:
                continue
            for field, value in result.items():
                if field not in batch.columns:
                    batch[field] = None  # Add new field if it does not exist
                # Ensure value is a string
                if isinstance(value, list):
                    value = convert_list_to_string(value)
                else:
                    value = str(value)
                try:
                    batch.at[idx, field] = value
                except Exception as e:
                    print(f"Failed to update index {idx}, field '{field}' with value '{value}': {e}")

        # Save the processed batch back to CSV incrementally
        if start == 0:
            batch.to_csv(output_path, mode='w', index=False, header=True)  # Write header only in first batch
        else:
            batch.to_csv(output_path, mode='a', index=False, header=False)  # Append without header for subsequent batches

        logging.info(f"Processed batch from {start} to {end - 1}. Data saved to {output_path}")

    logging.info("All data has been processed and saved.")


def process_row(row, fields_dict, external_data, model_name, url_field_name=False):
    """
    Process a contact by generating a prompt and calling an API model.

    Parameters:
        row (pd.Series): DataFrame row containing contact information.
        fields_dict (dict): Dictionary of fields and their descriptions.
        external_data (dict): Additional external data required for generating the prompt.
        model_name (str): Model identifier for the API call.

    Returns:
        pd.Series: A pandas Series with processed API response fields.
    """
    if pd.isna(row[list(fields_dict.keys())[-1]]):
        fields_empty = True
    else:
        fields_empty = False

    if fields_empty:
        try:
            row_data = row.drop(list(fields_dict.keys()))

            # Process URL
            if url_field_name:
                # Generate text content for URL
                content = get_text_content(row[url_field_name])
                # Append content to external_data
                external_data['URL Content'] = content 
            
            # Build prompt
            prompt = build_prompt(fields_dict, row_data, external_data)

            # Call the API model with the prompt
            model = genai.GenerativeModel(model_name=model_name)
            response = call_gemini(model, prompt)

            # Convert the Gemini response to JSON format
            json_objects = extract_json(response.text)
            json_response = json_objects[0]

            # Parse the API response into a pandas Series
            field_values = pd.Series({field: json_response.get(field, '') for field in fields_dict.keys()})
            
            logging.info(f"Processed: {row.iat[0]}")
            return field_values

        except Exception as e:
            logging.error(f"Error in process_row: {e}")
            field_values = pd.Series({field: '' for field in fields_dict.keys()})
            return field_values
        
    else:
        logging.info(f"Skipping already processed row for {row.get('Website')}")
        return row[list(fields_dict.keys())]
