# file_utils.py
import csv
import os
import logging

logger = logging.getLogger(__name__)

def ensure_directories_exist():
    """
    Ensure necessary directories exist for the project.
    """
    directories = ["logs", "ANKI", "input_files"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")

def get_default_input_files():
    """
    List all input files in the 'input_files/' directory.
    """
    input_dir = os.path.join(os.getcwd(), "input_files")
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    logger.debug(f"Found input files: {files}")
    return files

def parse_input_file(input_file):
    """
    Parse the input file and return a list of rows.
    Handles Markdown pipe tables and skips non-table lines.
    """
    rows = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        headers = None
        for line in lines:
            line = line.strip()
            if not line or "|" not in line:
                continue

            if headers is None:
                headers = [h.strip() for h in line.split("|") if h.strip()]
                if not headers:
                    raise ValueError("No valid headers found in the input file.")
                continue

            if "---" in line:
                continue

            values = [v.strip() for v in line.split("|")[1:-1]]
            if len(values) == len(headers):
                rows.append(dict(zip(headers, values)))
            else:
                logger.warning(f"Mismatched row length: {values}")
    except Exception as e:
        logger.error(f"Error parsing input file: {e}")
    return rows


def validate_input_file(input_file):
    """
    Validate if the input file exists, is readable, and contains valid Markdown table formatting.

    Args:
        input_file (str): Path to the input file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")
    if not os.access(input_file, os.R_OK):
        raise PermissionError(f"Input file {input_file} is not readable.")

    # Check for valid Markdown table formatting
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if len(lines) < 2:
            # A valid table needs at least a header and one row
            return False

        headers = lines[0].strip()
        separator = lines[1].strip()

        # Validate header and separator
        if "|" not in headers or "---" not in separator:
            return False

        # Ensure rows have consistent pipe-separated values
        header_columns = [col.strip() for col in headers.split("|") if col.strip()]
        for line in lines[2:]:
            row_columns = [col.strip() for col in line.split("|") if col.strip()]
            if len(row_columns) != len(header_columns):
                return False

    return True

