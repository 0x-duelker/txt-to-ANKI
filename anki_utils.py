# anki_utils.py
# This module focuses on Anki deck creation and note management.
import genanki
import logging
import os
import random

logger = logging.getLogger(__name__)

# Function to create an Anki deck
def create_deck(deck_name):
    """
    Creates a new Anki deck with a unique ID and returns the deck object.

    Args:
        deck_name (str): Name of the Anki deck.

    Returns:
        genanki.Deck: Anki deck object.
    """
    deck_id = random.randint(1, 2**63 - 1)
    logger.debug(f"Creating deck with ID {deck_id} and name '{deck_name}'.")
    return genanki.Deck(deck_id, deck_name)

# Function to create a model for the Anki deck
def create_model():
    """
    Creates a simple Anki model for notes and returns the model object.

    Returns:
        genanki.Model: Anki model object.
    """
    model_id = random.randint(1, 2**63 - 1)
    logger.debug(f"Creating model with ID {model_id}.")
    return genanki.Model(
        model_id,
        "SimpleModel",
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

# Function to add a note to an Anki deck
def add_note_to_deck(deck, model, front_text, back_text, image_url=""):
    """
    Adds a note to the provided Anki deck.

    Args:
        deck (genanki.Deck): The Anki deck to which the note will be added.
        model (genanki.Model): The model for the note.
        front_text (str): Front text of the note.
        back_text (str): Back text of the note.
        image_url (str, optional): URL of the image to include. Defaults to "".
    """
    try:
        note = genanki.Note(
            model=model,
            fields=[front_text, back_text, image_url],
        )
        deck.add_note(note)
        logger.debug(f"Note added - Front: {front_text}, Back: {back_text}, Image URL: {image_url}")
    except Exception as e:
        logger.error(f"Error adding note to deck: {e}")

# Function to export the Anki deck to a file
def export_deck(deck, output_filename):
    """
    Exports the provided Anki deck to a .apkg file.

    Args:
        deck (genanki.Deck): The Anki deck to export.
        output_filename (str): The path to save the exported .apkg file.
    """
    try:
        if not os.path.exists(os.path.dirname(output_filename)):
            os.makedirs(os.path.dirname(output_filename))
        package = genanki.Package(deck)
        package.write_to_file(output_filename)
        logger.info(f"Deck exported successfully to {output_filename}")
    except Exception as e:
        logger.error(f"Error exporting Anki deck: {e}")
