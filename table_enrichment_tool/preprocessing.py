import pandas as pd
import hashlib
import base64


def generate_unique_id(row, seed, fields, prefix="", length=16):
    """
    Generate a unique ID for a given row based on specified fields and a seed.

    Args:
        row (pd.Series): The row of the DataFrame.
        seed (str): The seed string used to ensure deterministic ID generation.
        fields (list): List of fields to use for ID generation.
        length (int): Desired length of the generated ID (default is 16).

    Returns:
        str: The generated unique ID with a prefix.
    """
    # Concatenate specified fields to create a unique string
    unique_string = ''.join(str(row[field]) for field in fields if pd.notna(row[field])) + seed
    # Generate a hash of the unique string
    hash_digest = hashlib.sha256(unique_string.encode()).digest()
    # Encode the hash in base64 and truncate/pad to ensure consistent length
    base64_encoded = base64.urlsafe_b64encode(hash_digest).decode('utf-8')[:length]
    # Ensure the ID is prefixed with "CON"
    return f"{prefix}{base64_encoded}"


def anonymize_rows(file_path, output_path, seed, personal_info_fields, id_fields, prefix=""):
    """
    Anonymize the row information in a CSV file by generating unique IDs and removing personal info fields.

    Args:
        file_path (str): Path to the input CSV file containing contact information.
        output_path (str): Path to the output CSV file to save anonymized contact information.
        seed (str): The seed string used to ensure deterministic ID generation.
        personal_info_fields (list): List of fields containing personal information to be removed.
        id_fields (list): List of fields to use for generating unique IDs.

    Returns:
        None
    """
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Generate unique ID for each contact
    df['ID'] = df.apply(lambda row: generate_unique_id(row, seed, id_fields, prefix), axis=1)
    
    # Save the original DataFrame with IDs to a new CSV file
    df.to_csv(file_path, index=False)
    
    # Remove personal information fields
    df_anonymized = df.drop(columns=personal_info_fields)
    
    # Save the modified DataFrame to a new CSV file
    df_anonymized.to_csv(output_path, index=False)


def de_anonymize_rows(original_path, anonymized_path, output_path, personal_info_fields, id_field='ID'):
    """
    Merge the original and anonymized CSV files based on the ID field and include specified personal fields.

    Args:
        original_file_path (str): Path to the original CSV file containing personal information.
        anonymized_file_path (str): Path to the anonymized CSV file.
        output_path (str): Path to the output CSV file to save the merged information.
        personal_info_fields (list): List of personal information fields to include in the merged file.
        id_field (str): The ID field to use for merging the files (default is 'ID').

    Returns:
        None
    """
    # Read the original and anonymized CSV files
    original_df = pd.read_csv(original_path)
    anonymized_df = pd.read_csv(anonymized_path)
    
    # Select the specified personal information fields and the ID field from the original DataFrame
    original_selected_df = original_df[[id_field] + personal_info_fields]
    
    # Merge the selected fields from the original DataFrame with the anonymized DataFrame
    merged_df = pd.merge(anonymized_df, original_selected_df, on=id_field, how='left')
    
    # Save the merged DataFrame to the specified output path
    merged_df.to_csv(output_path, index=False)