import requests
import shelve
import time
import os
import json
import logging
from hashlib import sha256
from utils import apply_nlp_refinement, expand_with_synonyms
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import aiohttp
import asyncio

used_images = set()

logger = logging.getLogger(__name__)
logger.debug("Execution started in pixabay_api.py")
logger.debug(f"Requests module loaded: {requests}")

CONFIG_FILE = "config.json"
CACHE_FILE = "pixabay_cache.db"
CACHE_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds
logger = logging.getLogger(__name__)



def add_image_to_note(image_url, note):
    if image_url not in used_images:
        used_images.add(image_url)
        # Add the image to the note
        note.add_image(image_url)
    else:
        # Handle the case where the image is a duplicate
        print(f"Duplicate image found: {image_url}")

class PixabayAPIError(Exception):
    pass

async def perform_pixabay_request_async(url, params, expanded_query, cache_key, cache, config):
    async with aiohttp.ClientSession() as session:
        try:
            if not isinstance(params, dict):
                logger.error(f"Invalid params type: Expected dict, got {type(params).__name__}. Content: {params}")
                return None, None

            async with session.get(url, params=params, timeout=5) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    return None, None

                response.raise_for_status()
                data = await response.json()
                if not isinstance(data, dict):
                    logger.error(f"Unexpected response type: {type(data).__name__}. Content: {data}")
                    return None, None
                logger.debug(f"Query '{params['q']}' returned {len(data.get('hits', []))} results.")

                if len(data.get("hits", [])) < 3 and config["strict_filters"]:
                    logger.warning("Few results found. Relaxing strict filters...")
                    params.pop("editors_choice", None)
                    async with session.get(url, params=params, timeout=5) as response:
                        response.raise_for_status()
                        data = await response.json()

                if data.get("hits"):
                    return process_pixabay_hits(data, expanded_query, cache_key, cache, config)
                else:
                    logger.warning(f"No results for query '{expanded_query}' after trying synonyms.")
                    return None, None

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching image for query '{expanded_query}': {e}")
            return None, None

def generate_cache_key(query, params):
    serialized = f"{query}-{json.dumps(params, sort_keys=True)}"
    return sha256(serialized.encode()).hexdigest()

def clear_expired_cache_entries(cache):
    keys_to_delete = [key for key, entry in cache.items() if time.time() - entry["timestamp"] >= CACHE_EXPIRATION]
    for key in keys_to_delete:
        del cache[key]
    logger.debug(f"Cache cleaned. Removed {len(keys_to_delete)} expired entries.")

def enforce_cache_size_limit(cache, max_size=100):
    if len(cache) > max_size:
        sorted_cache = sorted(cache.items(), key=lambda item: item[1]["timestamp"])
        keys_to_delete = [key for key, _ in sorted_cache[:len(cache) - max_size]]
        for key in keys_to_delete:
            del cache[key]
        logger.debug(f"Cache size limit enforced. Removed {len(keys_to_delete)} oldest entries.")

def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("pixabay_api_key")
    logger.error("Config file not found or API key is missing.")
    return None

async def fetch_pixabay_image(query, synonym_dict=None, config=None):
    """
    Fetches an image URL and credit from Pixabay, using query expansion with synonyms if provided.

    Args:
        query (str): The search term for the image.
        synonym_dict (dict, optional): Dictionary of synonyms for query expansion.
        config (dict, optional): Configuration for feature toggles and settings.

    Returns:
        tuple: Image URL and image credit string if found, otherwise (None, None).
    """
    api_key = os.getenv("PIXABAY_API_KEY") or load_api_key()
    if not isinstance(query, str):
        logger.error(f"Invalid query type: Expected string, got {type(query).__name__}")
        return None, None

    if not isinstance(config, dict):
        logger.error(f"Invalid config type: Expected dict, got {type(config).__name__}")
        return None, None

    if not api_key:
        logger.error("Pixabay API Key is missing.")
        return None, None

    #Default configuration
    default_config = config or {
        "use_synonyms": True,
        "rank_by_metadata": True,
        "strict_filters": True,
        "apply_nlp": True,
        "tags": [],
        "metadata_filter": {
            "min_likes": 50,
            "min_downloads": 100,
            "min_views": 500,
            "min_comments": 10,
        }
    }
    # Merge the default configuration with the provided config
    config = {**default_config, **(config or {})}

    logger.debug(f"Effective configuration: {config}")
    import json
    logger.debug(f"Configuration: {json.dumps(config, indent=2)}")

    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "editors_choice": "true",
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 10,
        "order": "popular",
    }
    logger.info(f"Fetching images for query: {query}")

    if config["strict_filters"]:
        params["editors_choice"] = "true"

    if config["tags"]:
        params["q"] = " ".join(config["tags"])

    queries_to_try = expand_with_synonyms(query, synonym_dict) if config["use_synonyms"] else [query]

    if config["apply_nlp"]:
        queries_to_try = [apply_nlp_refinement(q) for q in queries_to_try]

    cache_key_base = generate_cache_key(query, params)

    async with aiohttp.ClientSession() as session:
         with shelve.open(CACHE_FILE) as cache:
            clear_expired_cache_entries(cache)

            for expanded_query in queries_to_try:
                params["q"] = expanded_query
                cache_key = f"{cache_key_base}-{expanded_query}"

                # Check cache for existing entry
                if cache_key in cache:
                    cached_entry = cache[cache_key]
                    if cached_entry["image_url"] not in used_images:
                        used_images.add(cached_entry["image_url"])
                        return cached_entry["image_url"], cached_entry["image_credit"]

                # Fetch new images
                try:
                    image_url, image_credit = await perform_pixabay_request_async(
                        url, params, expanded_query, cache_key, cache, config
                    )
                    if image_url and image_url not in used_images:
                        used_images.add(image_url)  # Avoid duplicates
                        enforce_cache_size_limit(cache)  # Keep cache size within limits
                        return image_url, image_credit
                except Exception as e:
                    logger.error(f"Error processing query '{expanded_query}': {e}")

    return None, None

def perform_pixabay_request(url, params, expanded_query, cache_key, cache, config):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        if not isinstance(params, dict):
            logger.error(f"Invalid params type: Expected dict, got {type(params).__name__}. Content: {params}")
            return None, None
        response = session.get(url, params=params, timeout=5)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            return None, None

        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            logger.error(f"Unexpected response type: {type(data).__name__}. Content: {data}")
            return None, None
        logger.debug(f"Query '{params['q']}' returned {len(data.get('hits', []))} results.")

        if len(data.get("hits", [])) < 3 and config["strict_filters"]:
            logger.warning("Few results found. Relaxing strict filters...")
            params.pop("editors_choice", None)
            response = session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

        if data.get("hits"):
            return process_pixabay_hits(data, expanded_query, cache_key, cache, config)
        else:
            logger.warning(f"No results for query '{expanded_query}' after trying synonyms.")
            return None, None

    except requests.RequestException as e:
        logger.error(f"Error fetching image for query '{expanded_query}': {e}")
        return None, None

def relax_metadata_criteria(config, factor=0.5):
    """
    Dynamically relax metadata criteria by reducing thresholds.
    Args:
        config (dict): The configuration dictionary.
        factor (float): The factor by which to reduce the thresholds.
    """
    for key in config["metadata_filter"]:
        config["metadata_filter"][key] = int(config["metadata_filter"][key] * factor)
    logger.info("Relaxed metadata criteria: %s", config["metadata_filter"])


def process_pixabay_hits(data, expanded_query, cache_key, cache, config):
    """
    Processes the hits returned from the Pixabay API, filters them based on metadata criteria,
    and ensures the selected image is unique.

    Args:
        data (dict): Response data from Pixabay API.
        expanded_query (str): The query used to fetch the results.
        cache_key (str): Key for caching the results.
        cache (dict): Cache storage for results.
        config (dict): Configuration settings, including metadata filters.

    Returns:
        tuple: A tuple containing the image URL and credit text if a valid image is found,
               otherwise (None, None).
    """
    hits = data.get("hits", [])

    # Rank images based on likes, downloads, and views
    ranked_images = sorted(
        hits,
        key=lambda x: (x.get("likes", 0), x.get("downloads", 0), x.get("views", 0)),
        reverse=True
    )

    # Debug log to show why images failed criteria
    for img in ranked_images:
        logger.debug(
            f"Image {img.get('id')} failed criteria: likes={img.get('likes', 0)}, "
            f"downloads={img.get('downloads', 0)}, views={img.get('views', 0)}, "
            f"used={img.get('webformatURL') in used_images}"
        )

    # Filter images based on metadata and uniqueness
    filtered_images = [
        img for img in ranked_images if
        img.get("likes", 0) >= config["metadata_filter"].get("min_likes", 0) and
        img.get("downloads", 0) >= config["metadata_filter"].get("min_downloads", 0) and
        img.get("views", 0) >= config["metadata_filter"].get("min_views", 0) and
        img.get("webformatURL") not in used_images
    ]

    if not filtered_images:
        logger.warning(f"No images passed metadata filters for query '{expanded_query}'.")
        return None, None

    # Select the top filtered image
    image_info = filtered_images[0]
    image_url = image_info.get("webformatURL")
    image_credit = f"Image by {image_info.get('user')} from Pixabay"

    # Add the image URL to the used images set to avoid duplicates
    used_images.add(image_url)

    # Cache the result
    cache[cache_key] = {
        "image_url": image_url,
        "image_credit": image_credit,
        "timestamp": time.time()
    }
    logger.debug(f"Fetched and cached result for '{expanded_query}'.")

    return image_url, image_credit
