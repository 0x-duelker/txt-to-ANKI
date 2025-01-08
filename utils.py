from datamuse import Datamuse
import os
import json
import logging

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

# Configure logger for the utils module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

CONFIG_FILE = "config.json"
datamuse_api = Datamuse()
SYNONYMS_FILE = "synonyms.json"

def save_api_key(api_key):
    """
    Save the Pixabay API key to the configuration file.
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    config["pixabay_api_key"] = api_key
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    logger.info("API key saved to config file.")

def load_api_key(config_file=CONFIG_FILE):
    """Load the API key from the config file."""
    if os.path.exists(config_file):
        config = load_config(config_file)
        return config.get("pixabay_api_key", None)
    return None

def load_config(file_path):
    """Load configuration from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Invalid config type: Expected dict, got invalid JSON.")
    if not isinstance(config, dict):
        raise ValueError("Invalid config type: Expected dict, got {}".format(type(config).__name__))
    return config


def clean_string(input_string):
    """
    Removes special characters and normalizes spaces in a string.
    """
    import re
    cleaned = re.sub(r"[^\w\s]", " ", input_string)  # Replace non-alphanumeric chars with spaces
    return re.sub(r"\s+", " ", cleaned).strip()  # Normalize spaces and trim

def normalize_query(query):
    """
    Normalizes a query string for use in API requests.
    """
    return clean_string(query).lower()

def load_synonym_dict(file_path="synonyms.json"):
    """
    Load the synonym dictionary from a JSON file.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Synonym file {file_path} not found. Using an empty dictionary.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return {}

def fetch_synonyms_online(word, max_results=5):
    """
    Fetch synonyms for a given word using python-datamuse with a timeout.f
    """
    import requests
    try:
        # Set a timeout for the request to prevent hanging indefinitely
        results = datamuse_api.words(rel_syn=word, max=max_results, timeout=5)  # Timeout set to 5 seconds
        return [entry['word'] for entry in results]
    except requests.exceptions.Timeout:
        logger.warning(f"Request to Datamuse API timed out for word: '{word}'.")
        return []
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching synonyms for '{word}': {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching synonyms for '{word}': {e}")
        return []


def update_synonyms_file(word, new_synonyms):
    """
    Update the synonyms.json file with new synonyms for a given word.
    """
    try:
        if os.path.exists(SYNONYMS_FILE):
            with open(SYNONYMS_FILE, "r") as file:
                synonyms = json.load(file)
        else:
            synonyms = {}

        if word not in synonyms:
            synonyms[word] = new_synonyms
        else:
            synonyms[word] = list(set(synonyms[word] + new_synonyms))  # Avoid duplicates

        with open(SYNONYMS_FILE, "w") as file:
            json.dump(synonyms, file, indent=4)
        logger.info(f"Updated synonyms.json with new synonyms for '{word}'.")
    except Exception as e:
        logger.error(f"Error updating synonyms file: {e}")

def validate_synonyms(word, synonyms):
    valid_synonyms = [syn for syn in synonyms if len(syn.split()) == 1]  # Example: Exclude multi-word synonyms
    logger.debug(f"Validated synonyms for '{word}': {valid_synonyms}")
    return valid_synonyms

def get_synonyms(word):
    """
    Get synonyms for a word, combining online lookups and local storage.
    """
    synonyms = load_synonym_dict()
    if word in synonyms:
        return synonyms[word]

    online_synonyms = validate_synonyms(word, fetch_synonyms_online(word))
    if online_synonyms:
        update_synonyms_file(word, online_synonyms)
        return online_synonyms
    return []

def expand_with_synonyms(query, synonym_dict):
    """
    Expands a query dynamically using synonyms from a provided dictionary.

    Parameters:
        query (str): The original query string.
        synonym_dict (dict): Dictionary of synonyms where keys are words and values are lists of synonyms.

    Returns:
        list: A list of expanded queries including synonyms.
    """
    words = query.split()
    expanded_queries = [query]  # Include the original query

    for i, word in enumerate(words):
        if word in synonym_dict:
            for synonym in synonym_dict[word]:
                new_query = words[:i] + [synonym] + words[i + 1:]
                expanded_queries.append(" ".join(new_query))

    return expanded_queries

def apply_nlp_refinement(query):
    """
    Refines the query using NLP techniques such as lemmatization or stemming.
    Args:
        query (str): The search query.
    Returns:
        str: Refined query.
    """
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    refined_query = " ".join(lemmatizer.lemmatize(word) for word in query.split() if word.lower() not in stop_words)
    logger.debug(f"Refined query: {refined_query}")
    return refined_query
