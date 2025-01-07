# txt-to-ANKI
 This script reads from a txt file and generates corresponding ANKI flashcards, while also fetching relevant images for the front card from Unsplash. Its mainly geared towards language learners.

# Anki Deck Generator with Pixabay Integration

## Overview
This project automates the creation of Anki decks from structured text input files, leveraging Pixabay's API to fetch relevant images dynamically. It is particularly useful for language learners or anyone creating visually-enhanced Anki cards.

## Features
- **Dynamic Image Search**: Fetches images from Pixabay based on card keywords and meanings.
- **Synonym-Based Query Expansion**: Enhances image search by dynamically generating synonyms for better matches.
- **Tag Filtering**: Filters Pixabay results using metadata tags for improved relevance.
- **High-Quality Prioritization**: Selects images with higher popularity scores from Pixabay.
- **Advanced NLP Query Expansion**: Utilizes natural language processing for better keyword generation.
- **Caching**: Reduces API calls by caching results locally for 24 hours.
- **Error Handling**: Logs skipped rows and API issues for manual review.
- **Customizable Output**: Generates Anki decks with formatted front and back content, including optional image URLs.

## Requirements
### Python Libraries
- `tkinter`: For file selection dialogs.
- `csv`: For reading input files.
- `requests`: For API requests.
- `genanki`: For Anki deck creation.
- `os`: For file system operations.
- `re`: For text processing.
- `json`: For handling API responses.
- `time`: For timestamp-based caching.
- `uuid`: For generating unique IDs.
- `shelve`: For local caching.
- `hashlib`: For generating cache keys.
- `tqdm`: For progress bars.
- `random`: For generating random deck IDs.
- `logging`: For logging processes.
- `nltk`: For dynamic synonym generation via WordNet.

### External Dependencies
- [Pixabay API Key](https://pixabay.com/api/docs/): Required for fetching images.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/anki-pixabay-generator.git
   cd anki-pixabay-generator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download NLTK resources:
   ```python
   import nltk
   nltk.download('wordnet')
   nltk.download('omw-1.4')
   ```
4. Add your Pixabay API key:
   Update the `PIXABAY_API_KEY` variable in the code.

## Usage
1. Run the script:
   ```bash
   python txt-to-anki.py
   ```
2. Select your input file (Markdown or CSV format) using the file dialog.
3. Enter a name for your Anki deck.
4. The script processes the input file, searches for images, and generates the Anki deck.
5. The output `.apkg` file is saved in the `ANKI` directory.

### Input File Format
The input file must be a Markdown or CSV table with the following structure:

| WORD         | CONJUGATIONS                | MEANING                | EXAMPLE SENTENCE (GERMAN)           |
|--------------|-----------------------------|------------------------|-------------------------------------|
| **werden**   | wird, wurde, **ist geworden** | to become              | *Sie ist leider krank geworden.*   |

### Output
The output deck will include:
- **Front**: The word or phrase.
- **Back**: Details such as conjugations, meaning, example sentence, and optional image credit.
- **Image**: Dynamically fetched from Pixabay (if available).

## Advanced Features
### Synonym-Based Query Expansion
Automatically fetches synonyms using WordNet to enhance search results when images are not initially found.

### Tag Filtering
Filters results based on metadata tags from Pixabay to improve relevance.

### Popularity-Based Selection
Prioritizes images with higher popularity scores for better visual quality.

### NLP Query Expansion (Planned)
Future versions will integrate NLP-based query refinement for enhanced keyword generation.

## Logs
All operations are logged to the `logs` directory, including skipped rows, API errors, and deck generation summaries.

## Roadmap
- [x] Add dynamic synonym generation
- [x] Implement tag-based filtering
- [ ] Integrate advanced NLP for query expansion
- [ ] Support additional input formats (e.g., Excel)

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- [Pixabay API](https://pixabay.com/api/docs/)
- [NLTK](https://www.nltk.org/)
- [Genanki Library](https://github.com/kerrickstaley/genanki)
