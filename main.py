import os
import re
import time
import logging
from datetime import datetime
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog

from file_utils import ensure_directories_exist, get_default_input_files, parse_input_file, validate_input_file
from pixabay_api import fetch_pixabay_image
from anki_utils import create_deck, add_note_to_deck, export_deck

# Configure Logging
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"anki_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Main script
if __name__ == "__main__":
    try:
        logger.info("Starting Anki deck creation process.")

        # Ensure necessary directories exist
        ensure_directories_exist()

        # Prompt for Pixabay API Key if not provided
        PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
        if not PIXABAY_API_KEY:
            PIXABAY_API_KEY = input("Enter your Pixabay API Key: ").strip()
            if not PIXABAY_API_KEY:
                logger.error("Pixabay API Key is required. Exiting.")
                exit(1)

        # Check for files in the input_files/ directory
        input_files = get_default_input_files()
        if input_files:
            print("Available input files in 'input_files/':")
            for idx, file in enumerate(input_files, start=1):
                print(f"{idx}. {file}")
            file_choice = input("Enter the number of the file to process (or press Enter to choose manually): ").strip()

            if file_choice.isdigit() and 1 <= int(file_choice) <= len(input_files):
                input_file = os.path.join("input_files", input_files[int(file_choice) - 1])
                print(f"Selected file: {input_file}")
            else:
                input_file = filedialog.askopenfilename(
                    title="Select your Markdown/CSV input file",
                    initialdir=os.path.join(os.getcwd(), "input_files"),
                    filetypes=[("Text Files", "*.md *.markdown *.csv *.tsv *.txt"), ("All Files", "*.*")]
                )
        else:
            print("No files found in 'input_files/'. Please select a file manually.")
            input_file = filedialog.askopenfilename(
                title="Select your Markdown/CSV input file",
                initialdir=os.path.join(os.getcwd(), "input_files"),
                filetypes=[("Text Files", "*.md *.markdown *.csv *.tsv *.txt"), ("All Files", "*.*")]
            )

        if not input_file:
            logger.error("No file selected. Exiting.")
            exit(1)

        # Validate input file
        if not validate_input_file(input_file):
            logger.error("Invalid input file format. Exiting.")
            exit(1)

        # Prompt for Anki deck name
        deck_name = input("Enter the name for your Anki deck: ").strip()
        if not deck_name:
            logger.error("Deck name is required. Exiting.")
            exit(1)
        deck_name = re.sub(r"[^\w\s]", "", deck_name).strip()
        if not deck_name:
            logger.error("Invalid deck name. Exiting.")
            exit(1)

        # Create Anki deck
        logger.info("Creating Anki deck...")
        my_deck = create_deck(deck_name)

        # Parse input file
        logger.info("Parsing input file...")
        rows = parse_input_file(input_file)
        if not rows:
            logger.error("No valid rows found in the input file. Exiting.")
            exit(1)

        # Process rows and add notes
        skipped_rows = []
        for idx, row in enumerate(tqdm(rows, desc="Processing rows")):
            try:
                front_text = row.get("WORD") or row.get("Front")
                if not front_text:
                    skipped_rows.append(row)
                    continue

                front_text = front_text.strip()
                raw_query = row.get("MEANING", "").strip()
                query = re.sub(r"[^\w\s]", " ", raw_query).strip()
                query = re.sub(r"\s+", " ", query)  # Normalize spaces

                image_url, image_credit = fetch_pixabay_image(query, PIXABAY_API_KEY)

                back_parts = []
                for k, v in row.items():
                    if k.lower() not in ["word", "front"] and v:
                        back_parts.append(f"<b>{k}:</b> {v.strip()}")
                if image_credit:
                    back_parts.append(f"<b>Image Credit:</b> {image_credit}")

                back_text = "<br>".join(back_parts)
                add_note_to_deck(my_deck, front_text, back_text, image_url)

            except Exception as e:
                logger.error(f"Error processing row {idx + 1}: {e}")
                skipped_rows.append(row)

        # Export deck
        output_dir = os.path.join(os.getcwd(), "ANKI")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{deck_name}.apkg")
        logger.info("Exporting Anki deck...")
        export_deck(my_deck, output_path)

        logger.info(f"Anki deck created successfully! Saved to {output_path}")
        if skipped_rows:
            logger.warning(f"Skipped {len(skipped_rows)} rows. Check logs for details.")

    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        exit(1)
