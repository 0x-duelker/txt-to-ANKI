import tkinter as tk
from tkinter import filedialog
import csv
import requests
import genanki
import os
import re
import json
import time
import uuid
import shelve
from hashlib import sha256
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



PIXABAY_API_KEY = "48075518-5c8e3f88d3639f87f2db325c6"
CACHE_FILE = os.path.join(os.getcwd(), "pixabay_cache.db")
CACHE_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds

def generate_cache_key(query, params):
    """
    Generate a unique cache key for a query and its parameters.
    """
    serialized = f"{query}-{json.dumps(params, sort_keys=True)}"
    return sha256(serialized.encode()).hexdigest()

def fetch_pixabay_image(query):
    if not PIXABAY_API_KEY:
        logger.error("Pixabay API Key is missing.")
        return None, None

    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 1,
    }

    cache_key = generate_cache_key(query, params)

    with shelve.open(CACHE_FILE) as cache:
        try:
            keys_to_delete = [
                key for key, entry in cache.items()
                if time.time() - entry["timestamp"] >= CACHE_EXPIRATION
            ]
            for key in keys_to_delete:
                del cache[key]

            if cache_key in cache:
                cached_entry = cache[cache_key]
                if time.time() - cached_entry["timestamp"] < CACHE_EXPIRATION:
                    logger.debug(f"Cache hit for '{query}'.")
                    return cached_entry["image_url"], cached_entry["image_credit"]

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                return fetch_pixabay_image(query)  # Retry request

            response.raise_for_status()
            data = response.json()

            if data.get("hits"):
                image_info = data["hits"][0]
                image_url = image_info.get("webformatURL")
                image_credit = f"Image by {image_info.get('user')} from Pixabay"

                cache[cache_key] = {
                    "image_url": image_url,
                    "image_credit": image_credit,
                    "timestamp": time.time()
                }
                logger.debug(f"Fetched and cached result for '{query}'.")
                return image_url, image_credit

            logger.warning(f"No images found for '{query}'.")
            return None, None

        except requests.RequestException as e:
            logger.error(f"Error fetching Pixabay image for '{query}': {e}")
            return None, None


# Example Usage
if __name__ == "__main__":
    query = "yellow flower"
    image_url, image_credit = fetch_pixabay_image(query)
    if image_url:
        tqdm.write(f"Image URL: {image_url}")
        tqdm.write(f"Credit: {image_credit}")
def parse_input_file(input_file):
    """
    Parse the input file and return a list of rows.
    Handles Markdown pipe tables and skips non-table lines.
    """
    rows = []
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    headers = None
    for line in lines:
        line = line.strip()
        logger.debug(f"Processing line - {line}")  # Debug: Print each line

        # Skip empty or non-table lines
        if not line or not "|" in line:
            logger.debug("Skipping non-table line.")
            continue

        # Handle table headers
        if headers is None:
            headers = [h.strip() for h in line.split("|") if h.strip()]
            logger.debug(f" Found headers - {headers}")
            if not headers:  # Validate headers
                logger.error("ERROR: No valid headers found in the input file. Ensure the file has a valid table format.")
                return []
            continue

        # Skip separator lines (e.g., ---)
        if "---" in line:
            logger.debug(" Skipping separator line.")
            continue

        # Parse table row
        values = [v.strip() for v in line.split("|")[1:-1]]  # Exclude leading/trailing empty splits
        if len(values) == len(headers):
            row = dict(zip(headers, values))
            rows.append(row)
            logger.debug(f"Parsed row - {row}")  # Debug: Print parsed row
        else:
            logger.warning(f"WARNING: Mismatched row length. Headers: {len(headers)}, Values: {len(values)} - {values}")
    
    logger.debug(f"Total rows parsed - {len(rows)}")
    return rows


def main():
    root = tk.Tk()
    root.withdraw()

    # File dialog for input file
    input_file = filedialog.askopenfilename(
        title="Select your Markdown/CSV input file",
        filetypes=[("Text Files", "*.md *.markdown *.csv *.tsv *.txt"), ("All Files", "*.*")]
    )
    if not input_file:
        tqdm.write("No file selected. Exiting.")
        return

    # Prompt for deck and filename
    deck_name = input("Enter the name for your Anki deck (it will also be used as the filename): ").strip()
    if not deck_name:
        tqdm.write("Deck name is required. Exiting.")
        return

    #Validate Deck Name Input
    deck_name = re.sub(r"[^\w\s]", "", deck_name).strip()  # Remove invalid characters
    if not deck_name:
        tqdm.write("Invalid deck name. Exiting.")
        return

    # Ensure /ANKI subdirectory exists
    anki_dir = os.path.join(os.getcwd(), "ANKI")
    os.makedirs(anki_dir, exist_ok=True)

    # Adjust output_filename to save in /ANKI
    output_filename = os.path.join(anki_dir, f"{deck_name}.apkg")

    # Create an Anki deck
    my_deck = genanki.Deck(deck_id=random.randint(1, 2**63 - 1), name=deck_name)
    my_model = genanki.Model(
        model_id=random.randint(1, 2**63 - 1),
        name="MySimpleModel",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
            {"name": "ImageURL"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}<br><br>{{#ImageURL}}<img src='{{ImageURL}}'><br>{{/ImageURL}}",
                "afmt": "{{Front}}<hr id='answer'>{{Back}}",
            },
        ],
    )
    #Improved output file validation(?)
    try:
        my_package = genanki.Package(my_deck)
        logger.debug(f"Total notes in deck - {len(my_deck.notes)}")  # Debug total notes
        tqdm.write(f"Generating Anki deck: {output_filename}")
        my_package.write_to_file(output_filename)
        
        if not os.path.exists(output_filename):  # Ensure file was saved
            logger.error(f"ERROR: Failed to create the Anki deck at {output_filename}.")
            return
        tqdm.write(f"Anki deck created successfully! Saved to {output_filename}")
    except Exception as e:
        logger.error(f"Error exporting Anki deck: {e}")

    # Parse the input file
    try:
        rows = parse_input_file(input_file)
    except Exception as e:
        logger.error(f"Error parsing input file: {e}")
        return

    for idx, row in enumerate(tqdm(rows, desc="Processing rows")):
        try:
            # Extract the front text
            logger.debug(f"Processing row {idx + 1}/{len(rows)}: {row}")  # Add progress tracking

            front_text = row.get("WORD") or row.get("Front") or None
            if not front_text:
                tqdm.write(f"Skipping row with no valid 'WORD' or 'Front': {row}")
                continue

            front_text = front_text.strip()

            # Fetch image from Pixabay if needed
            image_url, image_credit = fetch_pixabay_image(front_text)
            logger.debug(f"Fetched image URL: {image_url}")  # Debug fetched image

            # Initialize the back text parts
            back_parts = []
            for k, v in row.items():
                if k.lower() == "word" or k.lower() == "front":
                    continue
                if v:  # Skip empty values
                    back_parts.append(f"<b>{k}:</b> {v.strip()}")

            if image_credit:
                back_parts.append(f"<b>Image Credit:</b> {image_credit}")

            # Ensure there's something in the back text
            if not back_parts:
                tqdm.write(f"Skipping row with no valid back text: {row}")
                continue

            back_text = "<br>".join(back_parts)

            # Create the Anki note
            note = genanki.Note(
                model=my_model,
                fields=[front_text, back_text, image_url or ""],
            )
            my_deck.add_note(note)
            logger.debug(f"Note added - Front: {front_text}, Back: {back_text}, Image URL: {image_url}")  # Debug

        except Exception as e:
            logger.error(f"Error creating note for row {idx + 1}: {row} - {e}")  # Improved error context

if __name__ == "__main__":
    main()
