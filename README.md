# Gemini Table Enricher

## Overview

Gemini Table Enricher is a Python tool designed to enhance CSV files by enriching them with additional fields generated via the Gemini API.

## Features

- Load and process CSV files.
- Ensure all required columns exist.
- Batch processing of data.
- Parallel processing using multiple threads.
- Dynamic application of enrichment steps.
- Incremental saving of processed data.

## Prerequisites

- Python 3.10.10
- Required Python packages (listed in `requirements.txt`)
- Google Gemini API key (follow instructions [here](https://ai.google.dev/gemini-api/docs/api-key))

## Installation
1. Clone the repository:

   `git clone https://github.com/matt-house-e/gemini_table_enricher.git`
   `cd gemini_table_enricher`

2.  Install the required packages:
    
    `pip install -r requirements.txt`
    

Usage
-----

### Prepare Your Environment

1.  **Obtain a Gemini API Key**: Follow the instructions [here](https://ai.google.dev/gemini-api/docs/api-key) to obtain your API key. Store the API key in an environment variable called `GOOGLE_API_KEY`:
    
2.  **Prepare Your CSV File**: Ensure your CSV file is properly formatted and accessible.
    
3.  **Define the Field Dictionary**: Create a dictionary that maps the required fields to their descriptions for the API.
    
4.  **Set Up External Data**: Prepare any additional external data required for generating prompts. For external data that does not change between each row of the table, define it in the notebook. If the data changes between each row use the steps functionality.
    
5.  **Configure Enrichment Steps**: Define a list of steps, each containing a function and its parameters. Note that steps add information spcific to the row being processed to external data. For external data that remains consistent across the submissions to Gemini, it should not be added in steps, just defined in external data once in the notebook.
    

### Running the Tool in a Jupyter Notebook
See the example.ipynb for how to use the tool

## Enrichment Steps

----------------
#### `scrape_url_content`

Scrapes content from provided URL(s) and adds it to the external data dictionary.

**Parameters**:
*   `external_data` (dict): Dictionary to store external data.
*   `urls` (str or list): The URL(s) to fetch content from.

---------------
#### `find_sub_pages`

Finds sub-pages from the given base URL and adds the list to the external data dictionary.

**Parameters**:
*   `external_data` (dict): Dictionary to store external data.
*   `base_url` (str): The base URL to find sub-pages from.

---------------
#### `read_csv`

Adds the contents of the specified CSV file to the external data dictionary.

**Parameters**:
*   `external_data` (dict): Dictionary to store external data.
*   `file_path` (str): The file path to the CSV file.
*   `key` (str): The key under which to store the CSV data in `external_data`.

---------------
#### `read_pdf`

Reads a PDF file, extracts all its text, and adds it to the external data dictionary.

**Parameters**:
*   `external_data` (dict): Dictionary to store external data.
*   `file_path` (str): The file path to the PDF file.
*   `key` (str): The key under which to store the extracted text in `external_data`.

## Anonymizing Data
To protect personal information before submitting data to the Gemini API, you can anonymize the data using the following functions:

#### `generate_unique_id`

Generates a unique ID for a given row based on specified fields and a seed.

**Parameters**:
*   `row` (pd.Series): The row of the DataFrame.
*   `seed` (str): The seed string used to ensure deterministic ID generation.
*   `fields` (list): List of fields to use for ID generation.
*   `prefix` (str): Prefix for the generated ID.
*   `length` (int): Desired length of the generated ID (default is 16).

---------------
#### `anonymize_rows`

Anonymizes the row information in a CSV file by generating unique IDs and removing personal info fields.

**Parameters**:
*   `file_path` (str): Path to the input CSV file containing contact information.
*   `output_path` (str): Path to the output CSV file to save anonymized contact information.
*   `seed` (str): The seed string used to ensure deterministic ID generation.
*   `personal_info_fields` (list): List of fields containing personal information to be removed.
*   `id_fields` (list): List of fields to use for generating unique IDs.
*   `prefix` (str): Prefix for the generated ID.

---------------
#### `de_anonymize_rows`

Merges the original and anonymized CSV files based on the ID field and includes specified personal fields.

**Parameters**:
*   `original_file_path` (str): Path to the original CSV file containing personal information.
*   `anonymized_file_path` (str): Path to the anonymized CSV file.
*   `output_path` (str): Path to the output CSV file to save the merged information.
*   `personal_info_fields` (list): List of personal information fields to include in the merged file.
*   `id_field` (str): The ID field to use for merging the files (default is 'ID').

License
-------

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Contributing
------------

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct, and the process for submitting pull requests.

Note on Data Privacy
--------------------

To ensure the privacy of personal information, it is recommended to anonymize data before submitting it to the Gemini API. Use the provided functions to generate unique IDs and remove personal information fields from your data.