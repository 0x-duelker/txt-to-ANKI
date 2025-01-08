import logging
import os
import re
from datetime import datetime
from tkinter import filedialog
import asyncio
import json
import pixabay_api
import pexels_api

from tqdm import tqdm

from anki_utils import create_deck, add_note_to_deck, export_deck
from file_utils import get_default_input_files, parse_input_file, validate_input_file, save_config
from pixabay_api import fetch_pixabay_image
from utils import load_synonym_dict, get_synonyms, load_config

if hasattr(pixabay_api, "requests"):
    print("Requests module is available in pixabay_api.")
else:
    print("Requests module is NOT available in pixabay_api.")

# Constants
LOG_DIR = os.path.join(os.getcwd(), "logs")
CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json")
SYNONYM_DICT_PATH = "synonyms.json"
INPUT_FILES_DIR = os.path.join(os.getcwd(), "input_files")
OUTPUT_DIR = os.path.join(os.getcwd(), "ANKI")

# Configure Logging
def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

ensure_directories()

log_filename = os.path.join(LOG_DIR, f"anki_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),  # Logs to a file with a timestamped name
        logging.StreamHandler()            # Logs to the console
    ]
)
logger = logging.getLogger(__name__)
logging.info("Script started.")

def save_config(file_path, config):
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

def fetch_image(query, config):
    """
    Attempt to fetch an image using Pixabay, then fallback to Pexels.
    """
    cache_key = f"image-{query}"

    # Try Pixabay first
    image_url, image_credit = pixabay_api.fetch_pixabay_images(query, cache_key, pixabay_api.cache, config)
    if image_url:
        return image_url, image_credit

    # Fallback to Pexels
    logger.info(f"Falling back to Pexels for query '{query}'.")
    image_url, image_credit = pexels_api.fetch_pexels_images(query, cache_key, pexels_api.cache)
    if image_url:
        return image_url, image_credit

    logger.warning(f"No image found for query '{query}' using both APIs.")
    return None, None

def get_pixabay_api_key(config):
    """Load or prompt for the Pixabay API key."""
    api_key = config.get("pixabay_api_key")
    if not api_key:
        api_key = input("Enter your Pixabay API Key: ").strip()
        if api_key:
            config["pixabay_api_key"] = api_key
            save_config(CONFIG_FILE_PATH, config)
            logger.info("Pixabay API Key saved successfully to config.json.")
        else:
            logger.error("Pixabay API Key is required. Exiting.")
            exit(1)
    else:
        logger.info("Pixabay API Key loaded successfully from config.json.")
    return api_key

def select_input_file():
    """Select the input file."""
    input_files = get_default_input_files()
    if input_files:
        print("Available input files in 'input_files/':")
        for idx, file in enumerate(input_files, start=1):
            print(f"{idx}. {file}")
        file_choice = input("Enter the number of the file to process (or press Enter to choose manually): ").strip()
        if file_choice.isdigit() and 1 <= int(file_choice) <= len(input_files):
            return os.path.join(INPUT_FILES_DIR, input_files[int(file_choice) - 1])
    selected_file = filedialog.askopenfilename(
        title="Select your Markdown/CSV input file",
        initialdir=INPUT_FILES_DIR,
        filetypes=[("Text Files", "*.md *.markdown *.csv *.tsv *.txt"), ("All Files", "*.*")]
    )
    if not selected_file:
        logger.error("No file selected. Exiting.")
        exit(1)
    return selected_file

def get_deck_name():
    """Prompt for and validate the deck name."""
    deck_name = input("Enter the name for your Anki deck: ").strip()
    if not deck_name:
        logger.error("Deck name is required. Exiting.")
        exit(1)
    deck_name = re.sub(r"[^\w\s]", "", deck_name).strip()
    if not deck_name:
        logger.error("Invalid deck name. Exiting.")
        exit(1)
    return deck_name

async def main():
    """Main script function."""
    try:
        logger.info("Starting Anki deck creation process.")
        ensure_directories()

        config = load_config(CONFIG_FILE_PATH)
        if not isinstance(config, dict):
            logger.error(f"Invalid config type: Expected dict, got {type(config).__name__}. Exiting.")
            exit(1)
        pixabay_api_key = get_pixabay_api_key(config)

        input_file = select_input_file()
        if not input_file:
            logger.error("No file selected. Exiting.")
            exit(1)

        if not validate_input_file(input_file):
            logger.error("Invalid input file format. Exiting.")
            exit(1)

        deck_name = get_deck_name()

        logger.info("Creating Anki deck...")
        my_deck = create_deck(deck_name)

        logger.info("Parsing input file...")
        rows = parse_input_file(input_file)
        if not rows:
            logger.error("No valid rows found in the input file. Exiting.")
            exit(1)

        synonym_dict = load_synonym_dict(SYNONYM_DICT_PATH)
        skipped_rows = []
        for idx, row in enumerate(tqdm(rows, desc="Processing rows")):
            try:
                if not isinstance(row, dict):
                    logger.error(f"Invalid row format at index {idx + 1}: {row}")
                    skipped_rows.append(row)
                    continue

                front_text = row.get("WORD") or row.get("Front")
                if not front_text:
                    skipped_rows.append(row)
                    continue

                front_text = front_text.strip()
                raw_query = row.get("MEANING", "").strip()
                query = re.sub(r"[^\w\s]", " ", raw_query).strip()
                query = re.sub(r"\s+", " ", query)  # Normalize spaces
                synonyms = get_synonyms(query)
                expanded_queries = [query] + synonyms

                image_url, image_credit = None, None
                for expanded_query in expanded_queries:
                    logger.debug(f"Config before calling fetch_pixabay_image: {config}")
                    image_url, image_credit = await fetch_pixabay_image(expanded_query, synonym_dict=synonym_dict, config=config)
                    if image_url:
                        break

                if not image_url:
                    logging.warning("No suitable image found for any query.")

                back_parts = [f"<b>{k}:</b> {v.strip()}" for k, v in row.items() if k.lower() not in ["word", "front"] and v]
                if image_credit:
                    back_parts.append(f"<b>Image Credit:</b> {image_credit}")

                back_text = "<br>".join(back_parts)
                add_note_to_deck(my_deck, front_text, back_text, image_url)

            except Exception as e:
                logger.error(f"Error processing row {idx + 1}: {e}")
                skipped_rows.append(row)

        output_path = os.path.join(OUTPUT_DIR, f"{deck_name}.apkg")
        logger.info("Exporting Anki deck...")
        export_deck(my_deck, output_path)

        logger.info(f"Anki deck created successfully! Saved to {output_path}")
        if skipped_rows:
            logger.warning(f"Skipped {len(skipped_rows)} rows. Check logs for details.")

    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())