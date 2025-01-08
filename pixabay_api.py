# pixabay_api.py
# Module for managing API interactions with Pixabay

import requests
import shelve
import time
import os
import json
import logging
from utils import apply_nlp_refinement
from hashlib import sha256
from utils import expand_with_synonyms

CONFIG_FILE = "config.json"
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

def load_api_key():
    """
    Loads the Pixabay API key from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("pixabay_api_key")
    logger.error("Config file not found or API key is missing.")
    return None

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
    data = {"hits": []}  # Default to an empty hits list

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
        "metadata_filter": {
            "min_likes": 50,  # Minimum likes to include an image
            "min_downloads": 100,  # Minimum downloads to include an image
    }}
    logger.debug(f"Configuration: {config}")

    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "editors_choice": "true",
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 10,  # Increased to get more results for ranking
        "order": "popular",  # Prioritize popular images
    }
    logger.debug(f"Sending query to Pixabay with params: {params}")
    logging.info("Fetching images for query: %s", query)

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
        logger.debug(f"Refining query using NLP techniques: {query}")
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

                logger.debug(f"Sending query to Pixabay with params: {params}") #Query log
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
                    logger.debug(f"Query '{params['q']}' returned {len(data.get('hits', []))} results.")

                    if len(data.get("hits", [])) < 3 and config["strict_filters"]:
                        logger.warning("Few results found. Relaxing strict filters...")
                        params.pop("editors_choice", None)  # Remove the strict filter
                        response = requests.get(url, params=params, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        hits = data.get("hits", [])  # Safely fetch hits from data

                    if data.get("hits"):
                        logging.info("Received %d results for query: %s", len(data.get("hits", [])), query)
                        logger.debug(f"Found {len(data['hits'])} results for query '{expanded_query}'.")

                        # Extract and filter tags
                        hits = data.get("hits", [])  # Explicitly define hits from the response
                        all_tags = {tag.strip() for hit in hits for tag in hit.get("tags", "").split(", ")}
                        BLACKLIST_TAGS = {"photo", "image", "stock", "pictures"}
                        filtered_tags = [tag for tag in all_tags if tag.lower() not in BLACKLIST_TAGS]
                        config["tags"] = filtered_tags[:5]  # Limit to top 5 tags
                        logger.debug(f"Filtered tags for refinement: {config['tags']}")

                        # Optionally use the most common tags to refine the query
                        config["tags"] = list(filtered_tags)[:5]  # Example: Limit to top 5 tags
                        logger.debug(f"Refined tags for next queries: {config['tags']}")

                        # Rank images by likes, downloads, and views if enabled
                        ranked_images = (
                            sorted(
                                data["hits"],
                                key=lambda x: (x.get("likes", 0), x.get("downloads", 0), x.get("views", 0)),
                                reverse=True
                            ) if config["rank_by_metadata"] else data["hits"]
                        )

                        # Apply stricter metadata filtering
                        filtered_images = [
                            img for img in ranked_images
                            if img.get("likes", 0) >= config["metadata_filter"]["min_likes"]
                            and img.get("downloads", 0) >= config["metadata_filter"]["min_downloads"]
                        ]

                        # Log the filtering results
                        logger.debug(f"Filtered images: {len(filtered_images)} passed the criteria.")

                        if not filtered_images:
                            logger.warning("No images passed the metadata filtering criteria.")
                            return None, None

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
                    else:
                        logger.warning(f"No results for query '{query}' after trying synonyms.")

                except requests.RequestException as e:
                    logger.error(f"Error fetching image for query '{expanded_query}': {e}")

            if not data.get("hits"):
                logger.warning(f"No results for query '{params['q']}' with current filters.")
                logger.warning(f"No results for refined queries. Retrying with the original query: {query}")
                logger.warning(f"No results for query '{query}' after trying synonyms.")
                params["q"] = query
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                hits = data.get("hits", [])  # Safely fetch hits, even if it doesn't exist

            logger.warning(f"No images found for query '{query}' after trying synonyms.")
            return None, None

        except Exception as e:
            logger.error(f"Unexpected error during Pixabay fetch: {e}")
            return None, None