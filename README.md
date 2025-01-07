README

Project Overview

This project automates the creation of Anki flashcards enriched with images sourced from Pixabay. Key functionalities include:

Dynamic Query Expansion: Incorporates synonyms for richer search results.

API Configuration: Easily manage and update API keys.

Advanced Query Features:

NLP-based refinement.

Metadata-based ranking of results.

Strict filtering options.

Tag-based image searching.

Efficient Caching: Avoid redundant API calls by implementing cache mechanisms.

Logging and Debugging: Comprehensive logs ensure smooth monitoring and debugging.

Key Features

1. Dynamic Query Expansion

Synonym expansion powered by datamuse.

Local caching of synonyms to minimize redundant online lookups.

Configurable via synonyms.json file.

2. Pixabay Integration

Retrieves high-quality images based on the refined queries.

Advanced configuration options for filtering and sorting results.

3. NLP Query Refinement

Lemmatization ensures more relevant searches.

Configurable toggle to enable or disable NLP-based enhancements.

4. Metadata Ranking

Results are sorted by metadata attributes like likes, downloads, and views to ensure the best image is selected.

5. Strict Filters and Tags

Editor's choice filter for premium results.

Tag-based query support for precise searches.

6. Robust Logging

Detailed logs for:

Query expansions.

API requests and responses.

Cache hits, misses, and expirations.

Usage Instructions

Prerequisites

Install required Python libraries using:

pip install -r requirements.txt

Obtain a Pixabay API key from Pixabay.

Setting Up

Save the Pixabay API key:

python main.py --save-key YOUR_API_KEY

#### Handling Missing Images
- The system dynamically relaxes strict filters if results are limited.
- Logs provide detailed insights into fallback queries and their results.


Configure config.json:
{
    "use_synonyms": true,
    "rank_by_metadata": true,
    "strict_filters": true,  // Note: This can be dynamically relaxed.
    "apply_nlp": true,
    "tags": ["education", "learning"]
}

Run the application:

python main.py

Logging

Logs are saved in the logs/ directory for debugging purposes.

Testing

To verify feature integration:

Toggle feature settings in config.json.

Observe logs to ensure all layers are working together harmoniously.

Use sample queries to validate:

Synonym expansion.

Metadata ranking.

Tag filtering.

Future Improvements

Diversify image sourcing with additional APIs.

Optimize performance for large datasets and complex queries.

Enhance NLP processing with contextual understanding.

- Test how fallback queries perform by deliberately using strict filters or unlikely search terms.
- Review logs to ensure appropriate fallback strategies are applied and that the original query is attempted.

Changelog

Version 1.3

Integrated NLP-based query refinement.

Added tag-based filtering and stricter search controls.

Improved metadata-based ranking.

Introduced dynamic fallback mechanisms for handling limited results. 

Validated synonyms for query expansion to reduce irrelevant results.


Version 1.2

Implemented dynamic synonym expansion using datamuse.

Introduced caching for synonyms and API responses.

Version 1.1

Added Pixabay integration for fetching images.

Basic query normalization and logging setup.

Version 1.0

Initial release with Anki deck generation and basic functionality.

