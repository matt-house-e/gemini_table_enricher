Gemini Table Enricher
Overview
Gemini Table Enricher is a Python tool designed to enhance CSV files by enriching them with additional contact information via the Gemini API. It processes the data in batches, ensuring that updates are saved incrementally to prevent data loss.

Features
Load and process CSV files.
Ensure all required columns exist.
Batch processing of data.
Parallel processing using multiple threads.
Dynamic application of enrichment steps.
Incremental saving of processed data.
Prerequisites
Python 3.10.10
Required Python packages (listed in requirements.txt)
Google Gemini API key (follow instructions here)
Installation
Clone the repository:

sh
Copy code
git clone https://github.com/matt-house-e/gemini_table_enricher.git
cd gemini_table_enricher
Install the required packages:

sh
Copy code
pip install -r requirements.txt
Usage
Prepare Your Environment
Obtain a Gemini API Key: Follow the instructions here to obtain your API key.

Prepare Your CSV File: Ensure your CSV file is properly formatted and accessible.

Define the Field Dictionary: Create a dictionary that maps the required fields to their descriptions for the API.

Set Up External Data: Prepare any additional external data required for generating prompts.

Configure Enrichment Steps: Define a list of steps, each containing a function and its parameters.

Running the Tool in a Jupyter Notebook
python
Copy code
import logging
import pandas as pd
from your_module import enrich_table  # Adjust the import according to your module structure

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define parameters
csv_path = 'path/to/your/input.csv'
output_path = 'path/to/your/output.csv'
fields_dict = {
    'Field1': 'Description of Field1',
    'Field2': 'Description of Field2',
    # Add more fields as needed
}
external_data = {
    # Add any external data needed for generating prompts
}
model_name = 'your-model-name'
steps = [
    {'function': scrape_url_content, 'params': {'urls': 'row["URL"]'}},
    {'function': find_sub_pages, 'params': {'base_url': 'row["Base URL"]'}},
    {'function': read_csv, 'params': {'file_path': 'row["CSV File Path"]', 'key': 'row["CSV Key"]'}},
    {'function': read_pdf, 'params': {'file_path': 'row["PDF File Path"]', 'key': 'row["PDF Key"]'}},
    # Add more steps as needed
]

# Run the enrichment process
enrich_table(csv_path, output_path, fields_dict, external_data, model_name, steps, batch_size=10, max_workers=4)
Enrichment Steps
scrape_url_content
Scrapes content from provided URL(s) and adds it to the external data dictionary.

Parameters:

external_data (dict): Dictionary to store external data.
urls (str or list): The URL(s) to fetch content from.
find_sub_pages
Finds sub-pages from the given base URL and adds the list to the external data dictionary.

Parameters:

external_data (dict): Dictionary to store external data.
base_url (str): The base URL to find sub-pages from.
read_csv
Adds the contents of the specified CSV file to the external data dictionary.

Parameters:

external_data (dict): Dictionary to store external data.
file_path (str): The file path to the CSV file.
key (str): The key under which to store the CSV data in external_data.
read_pdf
Reads a PDF file, extracts all its text, and adds it to the external data dictionary.

Parameters:

external_data (dict): Dictionary to store external data.
file_path (str): The file path to the PDF file.
key (str): The key under which to store the extracted text in external_data.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Contributing
Please read CONTRIBUTING.md for details on the code of conduct, and the process for submitting pull requests.







