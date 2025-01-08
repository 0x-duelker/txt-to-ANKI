# README

## Introduction
Welcome to the Anki Flashcard Automation Tool! This project is designed to simplify the creation of engaging, visually enriched Anki flashcards by automating the process of sourcing high-quality images and integrating them with your vocabulary or learning material. Whether you are a student, educator, or lifelong learner, this tool provides an efficient and seamless way to enhance your flashcards.

With advanced features like synonym-based query expansion, natural language processing (NLP) enhancements, and metadata-driven image ranking, this tool ensures that every flashcard is both accurate and visually appealing. By leveraging the Pixabay API and intelligent search techniques, we bring together functionality and creativity to take your learning experience to the next level.

## Project Overview
This project automates the creation of Anki flashcards enriched with images sourced from Pixabay. Key functionalities include:

1. **Dynamic Query Expansion**: Incorporates synonyms for richer search results.
2. **API Configuration**: Easily manage and update API keys.
3. **Advanced Query Features**:
    - NLP-based refinement.
    - Metadata-based ranking of results.
    - Strict filtering options.
    - Tag-based image searching.
4. **Efficient Caching**: Avoid redundant API calls by implementing cache mechanisms.
5. **Logging and Debugging**: Comprehensive logs ensure smooth monitoring and debugging.

## Key Features

### 1. Dynamic Query Expansion
- Synonym expansion powered by `datamuse`.
- Local caching of synonyms to minimize redundant online lookups.
- Configurable via `synonyms.json` file.

### 2. Pixabay Integration
- Retrieves high-quality images based on the refined queries.
- Advanced configuration options for filtering and sorting results.

### 3. NLP Query Refinement
- Lemmatization ensures more relevant searches.
- Configurable toggle to enable or disable NLP-based enhancements.

### 4. Metadata Ranking
- Results are sorted by metadata attributes like likes, downloads, and views to ensure the best image is selected.

### 5. Strict Filters and Tags
- Editor's choice filter for premium results.
- Tag-based query support for precise searches.

### 6. Robust Logging
- Detailed logs for:
  - Query expansions.
  - API requests and responses.
  - Cache hits, misses, and expirations.

### 7. Fallback Mechanism
- Dynamically relaxes filters (e.g., removes `editors_choice`) to retrieve more results if the initial query yields too few images.

## Usage Instructions

### Prerequisites
- Install required Python libraries using:
  ```bash
  pip install -r requirements.txt
  ```
- Obtain a Pixabay API key from [Pixabay](https://pixabay.com/api/docs/).

### Setting Up
0. ## Configuration
    Copy `config.example.json` to `config.json`:
   ```bash
   cp config.example.json config.json

1. Save the Pixabay API key:
   ```bash
   python main.py --save-key YOUR_API_KEY
   ```
2. Configure `config.json`:
   ```json
   {
       "use_synonyms": true,
       "rank_by_metadata": true,
       "strict_filters": false,
       "apply_nlp": true,
       "tags": []
   }
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Logging
Logs are saved in the `logs/` directory for debugging purposes.

## Testing
To verify feature integration:
- Toggle feature settings in `config.json`.
- Observe logs to ensure all layers are working together harmoniously.
- Use sample queries to validate:
  - Synonym expansion.
  - Metadata ranking.
  - Tag filtering.

## Future Improvements
- Diversify image sourcing with additional APIs.
- Optimize performance for large datasets and complex queries.
- Enhance NLP processing with contextual understanding.

---

## Changelog

### Version 1.3
- Integrated NLP-based query refinement.
- Added tag-based filtering and stricter search controls.
- Improved metadata-based ranking.

### Version 1.2
- Implemented dynamic synonym expansion using `datamuse`.
- Introduced caching for synonyms and API responses.

### Version 1.1
- Added Pixabay integration for fetching images.
- Basic query normalization and logging setup.

### Version 1.0
- Initial release with Anki deck generation and basic functionality.
