import requests
import time
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Set for tracking used image URLs
used_images = set()

# Define cache to store results and avoid redundant API calls
cache = {}

# Load Pexels API Key from the config file
def load_api_key():
    import json
    with open("config.json", "r") as file:
        config = json.load(file)
    return config.get("pexels_api_key", "")

PEXELS_API_KEY = load_api_key()
PEXELS_API_URL = "https://api.pexels.com/v1/search"

def enforce_cache_size_limit(cache2, max_size=1000):
    """
    Ensure the cache does not exceed the specified size.
    """
    while len(cache2) > max_size:
        oldest_key = min(cache2, key=lambda k: cache2[k]["timestamp"])
        del cache2[oldest_key]

def fetch_pexels_images(query, cache_key, cache2):
    """
    Fetch images from Pexels API based on the query.
    """
    if cache_key in cache2:
        cached_entry = cache2[cache_key]
        if cached_entry["image_url"] not in used_images:
            used_images.add(cached_entry["image_url"])
            return cached_entry["image_url"], cached_entry["image_credit"]

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 15}

    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Pexels API request failed: {e}")
        return None, None

    hits = data.get("photos", [])
    if not hits:
        logger.warning(f"No results for query '{query}' on Pexels.")
        return None, None

    filtered_images = [
        img for img in hits
        if img.get("src", {}).get("medium") not in used_images
    ]

    if not filtered_images:
        logger.warning(f"No suitable image found for query '{query}' on Pexels.")
        return None, None

    # Select the first valid image
    selected_image = filtered_images[0]
    image_url = selected_image.get("src", {}).get("medium")
    photographer = selected_image.get("photographer")
    photo_url = selected_image.get("url")
    image_credit = f"Photo by {photographer} on <a href='{photo_url}'>Pexels</a>"

    used_images.add(image_url)
    cache2[cache_key] = {
        "image_url": image_url,
        "image_credit": image_credit,
        "timestamp": time.time(),
    }
    enforce_cache_size_limit(cache2)

    logger.debug(f"Fetched and cached result for '{query}' from Pexels.")
    return image_url, image_credit
