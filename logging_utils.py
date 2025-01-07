import logging
import os
from datetime import datetime

def setup_logging(log_dir="logs"):
    """
    Configures and sets up logging for the application.

    Args:
        log_dir (str): Directory to save log files.

    Returns:
        Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    log_filename = os.path.join(log_dir, f"anki_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Logs will be saved to: {log_filename}")
    return logger

def log_error(logger, message, exc_info=True):
    """
    Logs an error message.

    Args:
        logger (Logger): Logger instance to log the error.
        message (str): Error message to log.
        exc_info (bool): Whether to include exception traceback.
    """
    logger.error(message, exc_info=exc_info)
