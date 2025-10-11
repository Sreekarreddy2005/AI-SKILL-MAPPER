import pandas as pd
import re

def clean_text(text):
    """A simple function to clean text data."""
    if not isinstance(text, str):
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # You could add more cleaning steps here if needed (e.g., remove URLs, special characters)
    return text.strip()

def load_job_postings(filepath="data/LinkedIn_Jobs_Data_India.csv", description_column="description"):
    """
    Loads job postings from a CSV file into a pandas DataFrame.

    Args:
        filepath (str): The path to the CSV file.
        description_column (str): The name of the column containing the job description text.

    Returns:
        A list of cleaned job descriptions.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Successfully loaded {filepath}")
    except FileNotFoundError:
        print(f"Error: The file was not found at {filepath}")
        print("Please make sure you have downloaded the dataset and placed it in the 'data' directory.")
        return []

    if description_column not in df.columns:
        print(f"Error: The specified column '{description_column}' was not found in the CSV.")
        print(f"Available columns are: {df.columns.tolist()}")
        return []

    # Drop rows where the job description is missing
    df.dropna(subset=[description_column], inplace=True)

    # Clean the text in the description column
    df['cleaned_description'] = df[description_column].apply(clean_text)

    print(f"Loaded and cleaned {len(df)} job postings.")
    return df['cleaned_description'].tolist()

if __name__ == '__main__':
    # This part allows you to test the script directly
    job_descriptions = load_job_postings()
    if job_descriptions:
        print("\n--- Example of a Cleaned Job Description ---")
        print(job_descriptions[0][:500] + "...") # Print the first 500 characters of the first description