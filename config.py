import os
import logging
from dotenv import load_dotenv

def ensure_directories_exist():
    """Ensure required directories are created."""
    directories = ["logs", "ANKI", "input_files"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Load environment variables
load_dotenv()

# Logging setup
def setup_logging():
    """Set up centralized logging."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, "anki_processing.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized.")
    return logger

# Environment variable handling
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
if not PIXABAY_API_KEY:
    PIXABAY_API_KEY = input("Enter your Pixabay API Key: ").strip()
    if PIXABAY_API_KEY:
        with open(".env", "a") as env_file:
            env_file.write(f"PIXABAY_API_KEY={PIXABAY_API_KEY}\n")
    else:
        raise ValueError("Pixabay API Key is required.")

# Utility Functions
def clean_string(input_string):
    """Clean a string by removing special characters and normalizing spaces."""
    import re
    cleaned = re.sub(r"[^\w\s]", " ", input_string).strip()
    return re.sub(r"\s+", " ", cleaned)

if __name__ == "__main__":
    logger = setup_logging()

    # Ensure directories exist
    ensure_directories_exist()

    # Example usage of clean_string
    test_string = "Hello, World! Welcome to Python."
    logger.info(f"Cleaned string: {clean_string(test_string)}")

    # Test environment variable
    logger.info(f"Pixabay API Key: {PIXABAY_API_KEY}")
