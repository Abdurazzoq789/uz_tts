"""
Acronym and all-caps word processing for TTS.
Converts all-uppercase words to letter-by-letter spelling.
"""

from typing import Dict
from .logger import get_logger

logger = get_logger(__name__)


# Uzbek letter names in Cyrillic
LETTER_NAMES_CYRILLIC: Dict[str, str] = {
    'А': 'а',
    'Б': 'бе',
    'В': 'ве',
    'Г': 'ге',
    'Д': 'де',
    'Е': 'е',
    'Ё': 'ё',
    'Ж': 'же',
    'З': 'зе',
    'И': 'и',
    'Й': 'й',
    'К': 'ка',
    'Л': 'эл',
    'М': 'эм',
    'Н': 'эн',
    'О': 'о',
    'П': 'пе',
    'Р': 'эр',
    'С': 'эс',
    'Т': 'те',
    'У': 'у',
    'Ф': 'эф',
    'Х': 'ха',
    'Ҳ': 'ҳа',
    'Ц': 'це',
    'Ч': 'че',
    'Ш': 'ша',
    'Ъ': 'ъ',
    'Ь': 'ь',
    'Э': 'э',
    'Ю': 'ю',
    'Я': 'я',
    'Ғ': 'ға',
    'Қ': 'қа',
    'Ў': 'ў',
}

# Latin letter names (will be transliterated to Cyrillic later)
LETTER_NAMES_LATIN: Dict[str, str] = {
    'A': 'а',
    'B': 'бе',
    'C': 'се',
    'D': 'де',
    'E': 'е',
    'F': 'эф',
    'G': 'ге',
    'H': 'аш',
    'I': 'и',
    'J': 'же',
    'K': 'ка',
    'L': 'эл',
    'M': 'эм',
    'N': 'эн',
    'O': 'о',
    'P': 'пе',
    'Q': 'қа',
    'R': 'эр',
    'S': 'эс',
    'T': 'те',
    'U': 'у',
    'V': 'ве',
    'W': 'дабл ю',
    'X': 'экс',
    'Y': 'уай',
    'Z': 'зе',
}


def spell_out_acronym(word: str) -> str:
    """
    Spell out an acronym letter by letter.
    
    Args:
        word: All-caps word (e.g., "USA", "NATO")
    
    Returns:
        Letters spelled out separated by dashes
    
    Example:
        >>> spell_out_acronym("USA")
        "у-эс-а"
        >>> spell_out_acronym("НАТО")
        "эн-а-те-о"
    """
    letters = []
    
    for char in word:
        if char in LETTER_NAMES_CYRILLIC:
            letters.append(LETTER_NAMES_CYRILLIC[char])
        elif char in LETTER_NAMES_LATIN:
            letters.append(LETTER_NAMES_LATIN[char])
        else:
            # If character is not a letter, keep as-is
            letters.append(char.lower())
    
    return '-'.join(letters)


def process_acronyms_in_text(text: str) -> str:
    """
    Find and spell out all-caps words (acronyms) in text.
    Only processes words that are 2+ characters and ALL uppercase.
    
    Args:
        text: Text containing potential acronyms
    
    Returns:
        Text with acronyms spelled out
    
    Example:
        >>> process_acronyms_in_text("Men USA da yashayman")
        "Men у-эс-а da yashayman"
        >>> process_acronyms_in_text("НАТО tashkiloti")
        "эн-а-те-о tashkiloti"
    """
    import re
    
    def replace_acronym(match):
        word = match.group(0)
        
        # Only spell out if it's 2+ characters all uppercase
        # Exclude single capital letters (like "I" or "A")
        if len(word) >= 2 and word.isupper() and word.isalpha():
            spelled = spell_out_acronym(word)
            logger.debug(f"Spelling acronym: {word} → {spelled}")
            return spelled
        
        return word
    
    # Find all words (sequences of letters)
    # This will match both Latin and Cyrillic uppercase sequences
    result = re.sub(r'\b[A-ZА-ЯЁҚҒҲЎ]+\b', replace_acronym, text)
    return result
