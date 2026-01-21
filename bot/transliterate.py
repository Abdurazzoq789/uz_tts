"""
Uzbek Latin-to-Cyrillic transliteration.
Converts Uzbek Latin script (lotin) to Cyrillic script (krill) for TTS.
"""

from typing import Dict
from .logger import get_logger

logger = get_logger(__name__)


# Uzbek Latin to Cyrillic mapping
# Based on official Uzbek alphabet conversion standards
LATIN_TO_CYRILLIC: Dict[str, str] = {
    # Special characters (must come first for proper matching)
    "sh": "ш",
    "ch": "ч",
    "ng": "нг",
    "gh": "ғ",
    "o'": "ў",
    "g'": "ғ",
    "yo": "ё",
    "ya": "я",
    "ye": "е",
    
    # Capital special characters
    "Sh": "Ш",
    "Ch": "Ч",
    "Ng": "Нг",
    "Gh": "Ғ",
    "O'": "Ў",
    "G'": "Ғ",
    "Yo": "Ё",
    "Ya": "Я",
    "Ye": "Е",
    
    "SH": "Ш",
    "CH": "Ч",
    "NG": "НГ",
    "GH": "Ғ",
    "YO": "Ё",
    "YA": "Я",
    "YE": "Е",
    
    # Single characters
    "a": "а",
    "b": "б",
    "d": "д",
    "e": "е",
    "f": "ф",
    "g": "г",
    "h": "ҳ",
    "i": "и",
    "j": "ж",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "q": "қ",
    "r": "р",
    "s": "с",
    "t": "т",
    "u": "у",
    "v": "в",
    "x": "х",
    "y": "й",
    "z": "з",
    
    # Capital letters
    "A": "А",
    "B": "Б",
    "D": "Д",
    "E": "Е",
    "F": "Ф",
    "G": "Г",
    "H": "Ҳ",
    "I": "И",
    "J": "Ж",
    "K": "К",
    "L": "Л",
    "M": "М",
    "N": "Н",
    "O": "О",
    "P": "П",
    "Q": "Қ",
    "R": "Р",
    "S": "С",
    "T": "Т",
    "U": "У",
    "V": "В",
    "X": "Х",
    "Y": "Й",
    "Z": "З",
}


def latin_to_cyrillic(text: str) -> str:
    """
    Convert Uzbek Latin text to Cyrillic.
    
    Args:
        text: Uzbek text in Latin script
    
    Returns:
        Text converted to Cyrillic script
    
    Example:
        >>> latin_to_cyrillic("Salom dunyo!")
        "Салом дунё!"
    """
    result = text
    
    # Normalize different apostrophe types to standard '
    # In Uzbek, o' and g' are common, but people use different apostrophes
    apostrophe_variants = ["'", "'", "'", "`", "ʻ", "ʼ"]
    for variant in apostrophe_variants:
        result = result.replace(variant, "'")
    
    # Replace multi-character combinations first (sh, ch, etc.)
    # This is important to avoid incorrect conversions
    for latin, cyrillic in LATIN_TO_CYRILLIC.items():
        if len(latin) > 1:
            result = result.replace(latin, cyrillic)
    
    # Then replace single characters
    for latin, cyrillic in LATIN_TO_CYRILLIC.items():
        if len(latin) == 1:
            result = result.replace(latin, cyrillic)
    
    return result


def transliterate_if_latin(text: str) -> tuple[str, bool]:
    """
    Detect if text is Latin and transliterate to Cyrillic if needed.
    
    Args:
        text: Input text (Latin or Cyrillic)
    
    Returns:
        Tuple of (transliterated_text, was_latin)
    """
    # Count Cyrillic vs Latin characters
    cyrillic_count = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin_count = sum(1 for c in text if c.isalpha() and ('a' <= c.lower() <= 'z'))
    
    # If more Latin than Cyrillic, transliterate
    if latin_count > cyrillic_count:
        logger.info(f"Detected Latin script, transliterating to Cyrillic")
        transliterated = latin_to_cyrillic(text)
        logger.debug(f"Latin: {text[:50]}... → Cyrillic: {transliterated[:50]}...")
        return transliterated, True
    else:
        logger.info(f"Detected Cyrillic script, using as-is")
        return text, False
