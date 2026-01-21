"""
Text processing utilities for the Uzbek TTS Telegram Bot.
Handles hashtag removal, script detection, and text validation.
"""

import re
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


def remove_hashtag(text: str, hashtag: str) -> str:
    """
    Remove hashtag from text (case-insensitive).
    
    Args:
        text: Text containing hashtag
        hashtag: Hashtag to remove (e.g., "#audio")
    
    Returns:
        Text with hashtag removed and whitespace normalized
    """
    # Case-insensitive removal
    result = text.replace(hashtag, "")
    result = result.replace(hashtag.upper(), "")
    result = result.replace(hashtag.lower(), "")
    result = result.replace(hashtag.capitalize(), "")
    
    # Replace newlines with periods for natural pauses in speech
    result = result.replace('\n', '. ')
    result = result.replace('\r', '. ')
    
    # Normalize whitespace (remove extra spaces)
    result = ' '.join(result.split())
    
    # Clean up multiple periods
    while '..' in result:
        result = result.replace('..', '.')
    
    # Clean up period-space combinations
    result = result.replace('. . ', '. ')
    
    return result.strip()


def detect_script(text: str) -> str:
    """
    Detect if text is primarily Latin or Cyrillic script.
    This is used for logging/debugging purposes.
    
    Args:
        text: Text to analyze
    
    Returns:
        "Latin", "Cyrillic", or "Unknown"
    """
    # Count Cyrillic characters (Unicode range U+0400 to U+04FF)
    cyrillic_count = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    
    # Count Latin characters (a-z, A-Z)
    latin_count = sum(1 for c in text if c.isalpha() and ('a' <= c.lower() <= 'z'))
    
    # Determine dominant script
    if cyrillic_count > latin_count:
        return "Cyrillic"
    elif latin_count > 0:
        return "Latin"
    else:
        return "Unknown"


def validate_text(text: str) -> bool:
    """
    Validate that text is suitable for TTS.
    
    Args:
        text: Text to validate
    
    Returns:
        True if text is valid, False otherwise
    """
    # Check if text is empty or only whitespace
    if not text or not text.strip():
        logger.warning("Text is empty or contains only whitespace")
        return False
    
    # Check if text contains at least one letter
    if not any(c.isalpha() for c in text):
        logger.warning("Text contains no letters")
        return False
    
    return True


def process_text(text: str, hashtag: str) -> Optional[str]:
    """
    Complete text processing pipeline.
    
    Args:
        text: Original text from message
        hashtag: Hashtag to remove
    
    Returns:
        Processed text ready for TTS, or None if invalid
    """
    # Remove hashtag
    cleaned = remove_hashtag(text, hashtag)
    
    # Validate
    if not validate_text(cleaned):
        return None
    
    # Log detected script
    script = detect_script(cleaned)
    logger.info(f"Detected script: {script}, text length: {len(cleaned)}")
    
    return cleaned
