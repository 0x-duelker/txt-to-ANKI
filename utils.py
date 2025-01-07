from datamuse import Datamuse
import os
import re
import json
import logging

# Configure logger for the utils module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

CONFIG_FILE = "config.json"
datamuse_api = Datamuse()
SYNONYMS_FILE = "synonyms.json"

def save_api_key(api_key, config_file=CONFIG_FILE):
    """Save the API key to a config file."""
    config = load_config(config_file) if os.path.exists(config_file) else {}
    config["pixabay_api_key"] = api_key
    with open(config_file, "w") as f:
        json.dump(config, f)
    logger.debug("Pixabay API Key saved successfully.")

def load_api_key(config_file=CONFIG_FILE):
    """Load the API key from the config file."""
    if os.path.exists(config_file):
        config = load_config(config_file)
        return config.get("pixabay_api_key", None)
    return None

def load_config(config_file=CONFIG_FILE):
    """Load the configuration from the config file."""
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {}

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

def ensure_directories_exist():
    """
    Ensures necessary directories for the application exist.
    """
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ANKI", exist_ok=True)
    os.makedirs("input_files", exist_ok=True)

def save_config(config_file, data):
    """
    Saves configuration data to a JSON file.
    """
    import json
    with open(config_file, 'w') as file:
        json.dump(data, file, indent=4)

def load_config(config_file):
    """
    Loads configuration data from a JSON file.
    """
    import json
    import os
    if not os.path.exists(config_file):
        return {}
    with open(config_file, 'r') as file:
        return json.load(file)

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
    Fetch synonyms for a given word using python-datamuse.
    """
    try:
        results = datamuse_api.words(rel_syn=word, max=max_results)
        return [entry['word'] for entry in results]
    except Exception as e:
        logger.warning(f"Error fetching synonyms for '{word}': {e}")
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

def get_synonyms(word):
    """
    Get synonyms for a word, combining online lookups and local storage.
    """
    synonyms = load_synonym_dict()
    if word in synonyms:
        return synonyms[word]

    online_synonyms = fetch_synonyms_online(word)
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