import tkinter as tk
from tkinter import filedialog
import csv
import os
import requests
import genanki
import tempfile
import json

# Unsplash sample usage - you'll need your own Access Key:
UNSPLASH_ACCESS_KEY = "mMhNxUvNsZveO0o62pVjldzOxSJGAOGovJm0-iL34vI"

# We'll define a function to fetch an image from Unsplash given a word
def fetch_unsplash_image(query):
    """
    Example function to fetch an image from Unsplash for a given word/query.
    You MUST have your own valid API keys. This is just a placeholder.
    """
    if not UNSPLASH_ACCESS_KEY or "YOUR_UNSPLASH_ACCESS_KEY" in UNSPLASH_ACCESS_KEY:
        print("WARNING: No valid Unsplash Access Key provided. Returning None.")
        return None

    # Construct the API request
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "square",
        "per_page": 1,
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("results"):
            # Return the small or regular image url
            return data["results"][0]["urls"]["small"]
        else:
            return None
    except Exception as e:
        print(f"Error fetching from Unsplash: {e}")
        return None


def main():
    """
    1) Prompt user for input CSV/Markdown file.
    2) Ask for deck name.
    3) Ask for output .apkg filename.
    4) Parse the file, build a genanki deck, export to .apkg.
    """

    root = tk.Tk()
    root.withdraw()

    # Prompt for input file
    input_file = filedialog.askopenfilename(
        title="Select your Markdown/CSV input file",
        filetypes=[("Markdown/CSV", "*.md *.markdown *.csv *.tsv *.txt"), ("All Files", "*.*")]
    )
    if not input_file:
        print("No file selected. Exiting.")
        return

    # Prompt for deck name
    deck_name = input("Enter the name for your Anki deck (e.g. 'German Verbs'): ").strip()
    if not deck_name:
        print("No deck name specified. Exiting.")
        return

    # Prompt for output .apkg filename
    output_filename = input("Enter the desired output .apkg file name (e.g. 'GermanVerbs.apkg'): ").strip()
    if not output_filename.lower().endswith(".apkg"):
        output_filename += ".apkg"

    # Create a genanki deck
    # The deck_id can be any random number, but must be stable if you re-import.
    my_deck = genanki.Deck(deck_id=1234567890, name=deck_name)

    # A simple model for front/back + an optional "ImageURL" field
    # We'll store image HTML in the front if needed
    my_style_model = genanki.Model(
        model_id=1607392310,
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

    # Some helper to parse CSV or Markdown.
    # This example just checks if the file is CSV-like, or if it’s a pipe-delimited table from markdown.
    # Adjust as needed for your file’s actual format.

    rows = []
    # Attempt naive parse
    # If you’re reading from a Markdown pipe table, you might parse differently.
    # e.g. using '|' as delimiter or using regex. For simplicity, let's try CSV first:
    with open(input_file, "r", encoding="utf-8") as f:
        # A quick check: if the file has a pipe in its first line, we might try a different delimiter
        first_line = f.readline().strip()
        f.seek(0)
        if "|" in first_line:
            # Attempt pipe-delimited parse
            reader = csv.DictReader(f, delimiter="|")
            # DictReader can create keys like '' for blank columns, so let's filter them
            # We also must skip the table header line like: | Word | Meaning | ...
            # Because of the format: first & last columns might be empty strings from extra pipes
            for row in reader:
                # Filter out empty keys
                cleaned = {}
                for k in row.keys():
                    if k.strip():
                        # Use the stripped key as dictionary key
                        cleaned[k.strip()] = row[k].strip()
                rows.append(cleaned)
        else:
            # Attempt comma-delimited
            reader = csv.DictReader(f)
            for row in reader:
                # Just store it
                rows.append({k.strip(): v.strip() for k, v in row.items() if k})

    # If your data is actually more complicated, adjust the above parse logic.

    # Now build note for each row
    for row in rows:
        # FRONT - can come from either "Word" or "WORD"
        front_text = row.get("Word", "") or row.get("WORD", "")
        front_text = front_text.strip()

        # If no front text, skip
        if not front_text:
            print(f"Skipping row with empty 'Word': {row}")
            continue

        # Optionally fetch from Unsplash or from row for an image
        # e.g. if the user has an "Image" or "ImageURL" field, use that
        image_url = row.get("ImageURL", "").strip()
        if not image_url:
            # Let's try Unsplash
            possible_img = fetch_unsplash_image(front_text)
            if possible_img:
                image_url = possible_img

        # BACK
        back_parts = []
        for k, v in row.items():
            # We skip the 'word' field from the back
            if k.lower() == "word":
                continue
            # e.g. do "Meaning: to do xyz"
            back_parts.append(f"<b>{k}:</b> {v}")

        back_text = "<br>".join(back_parts)

        note = genanki.Note(
            model=my_style_model,
            fields=[front_text, back_text, image_url],  # The 3 fields in our model
        )
        my_deck.add_note(note)

    # Generate the final .apkg
    my_package = genanki.Package(my_deck)

    # You can optionally include any media files here:
    # my_package.media_files = ['audio1.mp3', 'some_image.jpg']

    # Export
    print(f"Building .apkg deck => {output_filename}")
    my_package.write_to_file(output_filename)
    print(f"Done! Created {output_filename}")


if __name__ == "__main__":
    main()
