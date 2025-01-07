# anki_utils.py
# This module focuses on Anki deck creation and note management.
import genanki
import logging
import os
import random

logger = logging.getLogger(__name__)

# Define a global model to use across all notes
GLOBAL_MODEL = genanki.Model(
    model_id=1234567890,  # Use a fixed model ID to ensure consistency
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

# Function to create an Anki deck
def create_deck(deck_name):
    """
    Creates an Anki deck with a given name.

    Args:
        deck_name (str): Name of the deck.

    Returns:
        genanki.Deck: Anki deck object.
    """
    try:
        deck_id = 123456789  # Use a fixed deck ID for consistency
        logger.debug(f"Creating deck with ID: {deck_id} and name: {deck_name}")
        return genanki.Deck(deck_id, deck_name)
    except Exception as e:
        logger.error(f"Error creating deck: {e}")
        raise

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
def add_note_to_deck(deck, front_text, back_text, image_url):
    """
    Adds a note to the provided Anki deck.

    Args:
        deck (genanki.Deck): Anki deck to add the note to.
        front_text (str): Front of the card.
        back_text (str): Back of the card.
        image_url (str): Optional image URL for the card.
    """
    try:
        note = genanki.Note(
            model=GLOBAL_MODEL,
            fields=[front_text, back_text, image_url or ""],
        )
        deck.add_note(note)
        logger.debug(f"Note added successfully: Front='{front_text}', Back='{back_text}'")
    except Exception as e:
        logger.error(f"Error adding note to deck: {e}")
        raise

# Function to export the Anki deck to a file
def export_deck(deck, output_path):
    """
    Exports the Anki deck to a file.

    Args:
        deck (genanki.Deck): Anki deck to export.
        output_path (str): Path to save the exported file.
    """
    try:
        logger.debug(f"Deck contains {len(deck.notes)} notes before export.")
        package = genanki.Package(deck)
        package.write_to_file(output_path)
        logger.info(f"Deck exported successfully to {output_path}")
    except Exception as e:
        logger.error(f"Error exporting deck: {e}")
        raise