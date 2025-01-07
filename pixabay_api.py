# pixabay_api.py
# Module for managing API interactions with Pixabay

import requests
import shelve
import time
import json
import logging
from hashlib import sha256

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
def fetch_pixabay_image(query, api_key):
    """
    Fetch an image URL and credit from Pixabay based on the query.

    Args:
        query (str): The search term for the image.
        api_key (str): Pixabay API key.

    Returns:
        tuple: Image URL and image credit string if found, otherwise (None, None).
    """
    if not api_key:
        logger.error("Pixabay API Key is missing.")
        return None, None

    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 3,
    }

    cache_key = generate_cache_key(query, params)

    with shelve.open(CACHE_FILE) as cache:
        try:
            # Clear expired cache entries
            keys_to_delete = [
                key for key, entry in cache.items()
                if time.time() - entry["timestamp"] >= CACHE_EXPIRATION
            ]
            for key in keys_to_delete:
                del cache[key]

            # Return cached result if available
            if cache_key in cache:
                cached_entry = cache[cache_key]
                logger.debug(f"Cache hit for '{query}'.")
                return cached_entry["image_url"], cached_entry["image_credit"]

            # Fetch from Pixabay API
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                return fetch_pixabay_image(query, api_key)  # Retry request

            response.raise_for_status()
            data = response.json()

            if data.get("hits"):
                image_info = data["hits"][0]
                image_url = image_info.get("webformatURL")
                image_credit = f"Image by {image_info.get('user')} from Pixabay"

                # Cache the result
                cache[cache_key] = {
                    "image_url": image_url,
                    "image_credit": image_credit,
                    "timestamp": time.time()
                }
                logger.debug(f"Fetched and cached result for '{query}'.")
                return image_url, image_credit

            logger.warning(f"No images found for '{query}'.")
            return None, None

        except requests.RequestException as e:
            logger.error(f"Error fetching Pixabay image for '{query}': {e}")
            return None, None
