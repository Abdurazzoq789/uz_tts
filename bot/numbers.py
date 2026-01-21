"""
Number-to-word conversion for Uzbek language.
Converts digits to Uzbek words for TTS.
"""

from typing import Dict


# Uzbek number words
ONES = {
    0: "",
    1: "бир",
    2: "икки",
    3: "уч",
    4: "тўрт",
    5: "беш",
    6: "олти",
    7: "етти",
    8: "саккиз",
    9: "тўққиз",
}

TENS = {
    10: "ўн",
    20: "йигирма",
    30: "ўттиз",
    40: "қирқ",
    50: "эллик",
    60: "олтмиш",
    70: "етмиш",
    80: "саксон",
    90: "тўқсон",
}

SCALES = {
    100: "юз",
    1000: "минг",
    1000000: "миллион",
    1000000000: "миллиард",
}


def number_to_uzbek_words(num: int) -> str:
    """
    Convert a number to Uzbek words.
    
    Args:
        num: Integer number (0-999999999)
    
    Returns:
        Uzbek word representation
    
    Example:
        >>> number_to_uzbek_words(42)
        "қирқ икки"
        >>> number_to_uzbek_words(2023)
        "икки минг йигирма уч"
    """
    if num == 0:
        return "нол"
    
    if num < 0:
        return "минус " + number_to_uzbek_words(abs(num))
    
    # Handle billions
    if num >= 1000000000:
        billions = num // 1000000000
        remainder = num % 1000000000
        result = number_to_uzbek_words(billions) + " миллиард"
        if remainder > 0:
            result += " " + number_to_uzbek_words(remainder)
        return result
    
    # Handle millions
    if num >= 1000000:
        millions = num // 1000000
        remainder = num % 1000000
        result = number_to_uzbek_words(millions) + " миллион"
        if remainder > 0:
            result += " " + number_to_uzbek_words(remainder)
        return result
    
    # Handle thousands
    if num >= 1000:
        thousands = num // 1000
        remainder = num % 1000
        if thousands == 1:
            result = "минг"
        else:
            result = number_to_uzbek_words(thousands) + " минг"
        if remainder > 0:
            result += " " + number_to_uzbek_words(remainder)
        return result
    
    # Handle hundreds
    if num >= 100:
        hundreds = num // 100
        remainder = num % 100
        if hundreds == 1:
            result = "юз"
        else:
            result = ONES[hundreds] + " юз"
        if remainder > 0:
            result += " " + number_to_uzbek_words(remainder)
        return result
    
    # Handle 10-99
    if num >= 10:
        tens_digit = (num // 10) * 10
        ones_digit = num % 10
        result = TENS[tens_digit]
        if ones_digit > 0:
            result += " " + ONES[ones_digit]
        return result
    
    # Handle 1-9
    return ONES[num]


def convert_numbers_in_text(text: str) -> str:
    """
    Convert all numbers in text to Uzbek words.
    Handles ordinal numbers (number followed by dash).
    
    Args:
        text: Text containing numbers
    
    Returns:
        Text with numbers converted to words
    
    Example:
        >>> convert_numbers_in_text("Men 25 yoshdaman")
        "Men йигирма беш yoshdaman"
        >>> convert_numbers_in_text("9-yanvar")
        "тўққиз инчи yanvar"
    """
    import re
    
    # First handle ordinal numbers (number + dash)
    def replace_ordinal(match):
        num_str = match.group(1)  # Just the number part
        try:
            num = int(num_str)
            return number_to_uzbek_words(num) + " инчи "
        except:
            return match.group(0)
    
    # Convert ordinals: "number-" → "number инчи "
    result = re.sub(r'(\d+)-', replace_ordinal, text)
    
    # Then handle regular numbers (integers and decimals)
    def replace_number(match):
        num_str = match.group(0)
        
        # Handle decimals
        if '.' in num_str or ',' in num_str:
            # Replace . or , with " вергул "
            num_str = num_str.replace('.', ' вергул ').replace(',', ' вергул ')
            parts = num_str.split(' вергул ')
            result = []
            for part in parts:
                if part.strip().isdigit():
                    result.append(number_to_uzbek_words(int(part.strip())))
                elif part == '':
                    result.append('вергул')
            return ' '.join(result)
        
        # Handle regular integers
        try:
            num = int(num_str)
            return number_to_uzbek_words(num)
        except:
            return num_str
    
    # Replace remaining numbers
    result = re.sub(r'\d+[.,]?\d*', replace_number, result)
    return result
