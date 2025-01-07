# file_utils.py
import csv
import os
import logging

logger = logging.getLogger(__name__)

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
    Validate if the input file exists and is readable.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")
    if not os.access(input_file, os.R_OK):
        raise PermissionError(f"Input file {input_file} is not readable.")
