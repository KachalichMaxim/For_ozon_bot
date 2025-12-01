"""Helper utility functions."""
import logging
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: str = "bot.log") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure logging to both file and console
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary values.
    
    Args:
        dictionary: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current if current is not None else default


def extract_offer_id_number(offer_id: str) -> Optional[int]:
    """
    Extract numeric value from offer_id for sorting.
    
    Removes 1-2 prefix symbols, then extracts first number (1-99).
    Numbers must be exactly 1-2 digits and not part of a larger number.
    
    Examples:
        "р20-п5-33" -> 20
        "р25-п5-33" -> 25
        "мд33-п2-30" -> 33
        "р1-п5-33" -> 1
        "р99-п5-33" -> 99
        "р100-п5-33" -> None (over 99, or part of 100)
        "invalid" -> None
    
    Args:
        offer_id: Offer ID string
        
    Returns:
        Extracted number (1-99) or None if not found/invalid
    """
    if not offer_id or not isinstance(offer_id, str):
        return None
    
    import re
    
    # Try removing 1 symbol prefix first
    if len(offer_id) > 1:
        without_prefix = offer_id[1:]
        # Match 1-2 digits followed by non-digit or end of string
        # This ensures we don't match "10" from "100"
        match = re.search(r'^(\d{1,2})(?:\D|$)', without_prefix)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 99:
                return num
    
    # Try removing 2 symbol prefix
    if len(offer_id) > 2:
        without_prefix = offer_id[2:]
        # Match 1-2 digits followed by non-digit or end of string
        match = re.search(r'^(\d{1,2})(?:\D|$)', without_prefix)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 99:
                return num
    
    # If no prefix removal worked, try to find number at start
    match = re.search(r'^(\d{1,2})(?:\D|$)', offer_id)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 99:
            return num
    
    return None

