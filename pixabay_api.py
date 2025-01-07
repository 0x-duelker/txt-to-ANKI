# pixabay_api.py
# Module for managing API interactions with Pixabay

import requests
import shelve
import time
import json
import logging
from hashlib import sha256
from utils import expand_with_synonyms

CACHE_FILE = "pixabay_cache.db"
CACHE_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds
logger = logging.getLogger(__name__)

# Function to generate a unique cache key
def generate_cache_key(query, params):
    """
    Generate a unique cache key for a query and its parameters.
    """
    serialized = f"{query}-{json.dumps(params, sort_keys=True)}"
    return sha256(serialized.encode()).hexdigest()

# Function to fetch an image from Pixabay
def fetch_pixabay_image(query, api_key, synonym_dict=None, config=None):
    """
    Fetches an image URL and credit from Pixabay, using query expansion with synonyms if provided.

    Args:
        query (str): The search term for the image.
        api_key (str): Pixabay API key.
        synonym_dict (dict, optional): Dictionary of synonyms for query expansion.
        config (dict, optional): Configuration for feature toggles and settings.

    Returns:
        tuple: Image URL and image credit string if found, otherwise (None, None).
    """
    if not api_key:
        logger.error("Pixabay API Key is missing.")
        return None, None

    # Default configuration
    config = config or {
        "use_synonyms": True,
        "rank_by_metadata": True,
        "strict_filters": True,
        "apply_nlp": True,
        "tags": [],  # Allow filtering by tags
    }

    logger.debug(f"Configuration: {config}")

    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 10,  # Increased to get more results for ranking
        "order": "popular",  # Prioritize popular images
    }

    if config["strict_filters"]:
        params.update({"editors_choice": "true"})  # Example of stricter filter
        logger.debug("Strict filters applied to query.")

    if config["tags"]:
        params.update({"q": " ".join(config["tags"])});
        logger.debug(f"Tags filter applied: {config['tags']}")

    # Expand query with synonyms if enabled
    queries_to_try = (expand_with_synonyms(query, synonym_dict)
                      if synonym_dict and config["use_synonyms"]
                      else [query])
    logger.debug(f"Queries to try: {queries_to_try}")

    if config["apply_nlp"]:
        queries_to_try = [apply_nlp_refinement(q) for q in queries_to_try]
        logger.debug(f"NLP-refined queries: {queries_to_try}")

    cache_key_base = generate_cache_key(query, params)

    with shelve.open(CACHE_FILE) as cache:
        try:
            # Clear expired cache entries
            keys_to_delete = [
                key for key, entry in cache.items()
                if time.time() - entry["timestamp"] >= CACHE_EXPIRATION
            ]
            for key in keys_to_delete:
                del cache[key]

            logger.debug(f"Cache cleaned. Removed {len(keys_to_delete)} expired entries.")

            # Iterate through expanded queries
            for expanded_query in queries_to_try:
                params["q"] = expanded_query
                cache_key = f"{cache_key_base}-{expanded_query}"
                logger.debug(f"Trying query: {expanded_query}")

                # Check cache
                if cache_key in cache:
                    cached_entry = cache[cache_key]
                    logger.debug(f"Cache hit for '{expanded_query}'.")
                    return cached_entry["image_url"], cached_entry["image_credit"]

                # Fetch from Pixabay API
                try:
                    response = requests.get(url, params=params, timeout=5)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue  # Retry the next query

                    response.raise_for_status()
                    data = response.json()

                    if data.get("hits"):
                        logger.debug(f"Found {len(data['hits'])} results for query '{expanded_query}'.")

                        # Rank images by likes, downloads, and views if enabled
                        ranked_images = (
                            sorted(
                                data["hits"],
                                key=lambda x: (x.get("likes", 0), x.get("downloads", 0), x.get("views", 0)),
                                reverse=True
                            ) if config["rank_by_metadata"] else data["hits"]
                        )

                        # Select the top-ranked image
                        image_info = ranked_images[0]
                        image_url = image_info.get("webformatURL")
                        image_credit = f"Image by {image_info.get('user')} from Pixabay"

                        # Cache the result
                        cache[cache_key] = {
                            "image_url": image_url,
                            "image_credit": image_credit,
                            "timestamp": time.time()
                        }
                        logger.debug(f"Fetched and cached result for '{expanded_query}'.")
                        return image_url, image_credit

                except requests.RequestException as e:
                    logger.error(f"Error fetching image for query '{expanded_query}': {e}")

            logger.warning(f"No images found for query '{query}' after trying synonyms.")
            return None, None

        except Exception as e:
            logger.error(f"Unexpected error during Pixabay fetch: {e}")
            return None, None




