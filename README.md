# Anki Deck Generator

This project generates Anki decks with flashcards from a Markdown/CSV input file, integrating images dynamically fetched from Pixabay.

## Features

### Core Functionality
- **Markdown/CSV Input Parsing**: Supports Markdown pipe tables or CSV-like inputs.
- **Dynamic Image Integration**: Fetches relevant images using Pixabay API for each note.
- **Anki Deck Creation**: Automatically generates `.apkg` Anki decks.
- **Logging**: Comprehensive logging for debugging and progress tracking.
- **Dynamic Synonyms**: Enhances image search accuracy by querying with dynamically matched synonyms (implemented).

### Modular Structure
This project is modularized for better maintainability and scalability:

1. **`file_utils.py`**
   - Handles file and directory operations.
   - Functions:
     - `ensure_directories_exist()`: Ensures required directories exist.
     - `parse_input_file()`: Parses the input file into rows.
     - `validate_input_file()`: Validates input file format.

2. **`pixabay_api.py`**
   - Manages API interactions with Pixabay.
   - Functions:
     - `fetch_pixabay_image()`: Fetches images from Pixabay.
     - `generate_cache_key()`: Generates unique cache keys for queries.

3. **`anki_utils.py`**
   - Manages Anki deck creation and note management.
   - Functions:
     - `create_deck()`: Initializes a new Anki deck.
     - `add_note_to_deck()`: Adds notes to the deck.
     - `export_deck()`: Exports the deck to `.apkg` format.

4. **`utils.py`**
   - Utility functions for string cleaning and configuration management.
   - Functions:
     - `clean_string()`: Removes special characters and normalizes spaces.
     - `normalize_query()`: Prepares query strings for API requests.
     - `save_config()`/`load_config()`: Saves and loads configurations.
     - `expand_with_synonyms()`: Expands queries dynamically using synonyms.

5. **`logging_utils.py`**
   - Centralized logging setup and management.
   - Functions:
     - `setup_logging()`: Configures logging for the project.

6. **`config.json`**
   - Stores persistent configuration values such as the Pixabay API key.

7. **`tests/`**
   - Directory for unit tests (to be implemented).

8. **Main Script (`main.py`):**
   - Orchestrates the workflow.
   - Handles user input and integrates functionalities from all modules.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Configuration**:
   - The script will prompt for the Pixabay API key on the first run and save it in `config.json`.

## Usage

1. **Prepare Input File**:
   - Place your Markdown/CSV file in the `input_files/` directory.

2. **Run the Script**:
   ```bash
   python main.py
   ```

3. **Follow Prompts**:
   - Select the input file.
   - Provide a name for the Anki deck.

4. **Import Deck to Anki**:
   - The generated `.apkg` file will be saved in the `ANKI/` directory.

## Development Roadmap

### Next Steps
1. **Pixabay Tag Filtering**:
   - Use metadata tags to improve image relevance.
2. **CLI Integration**:
   - Add `argparse` or `click` for a command-line interface.
3. **Testing Suite**:
   - Implement unit tests for all modules in the `tests/` directory.
4. **Advanced NLP Query Expansion**:
   - Leverage NLP libraries like `spaCy` or `NLTK` to enhance query construction.

## Contributing

Feel free to contribute by submitting issues or pull requests. Make sure to follow the project's coding guidelines.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- **Pixabay**: For providing free image resources.
- **Anki**: For their amazing spaced repetition software.
- **Python Libraries**: tqdm, requests, genanki, and more.
