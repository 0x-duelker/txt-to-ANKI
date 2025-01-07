import os
import re

def clean_string(input_string):
    """
    Removes special characters and normalizes spaces in a string.

    Args:
        input_string (str): String to clean.

    Returns:
        str: Cleaned string.
    """
    cleaned = re.sub(r"[^\w\s]", " ", input_string).strip()
    return re.sub(r"\s+", " ", cleaned)

def normalize_query(query):
    """
    Prepares a query string for API requests by cleaning and normalizing it.

    Args:
        query (str): Query string to normalize.

    Returns:
        str: Normalized query string.
    """
    return clean_string(query).lower()

def ensure_directories_exist():
    """
    Ensures necessary directories for the application exist.
    """
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ANKI", exist_ok=True)
    os.makedirs("input_files", exist_ok=True)
