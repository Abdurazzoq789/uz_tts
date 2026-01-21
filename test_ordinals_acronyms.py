"""
Test ordinal numbers and acronyms.
"""

from bot.numbers import convert_numbers_in_text
from bot.acronyms import spell_out_acronym, process_acronyms_in_text


def test_ordinal_numbers():
    """Test ordinal number conversion (number + dash)."""
    print("\n" + "="*60)
    print("Testing Ordinal Numbers (Number + Dash)")
    print("="*60 + "\n")
    
    test_cases = [
        ("9-yanvar", "тўққиз инчи yanvar", "9th January"),
        ("21-mart", "йигирма бир инчи mart", "21st March"),
        ("1-may", "бир инчи may", "1st May"),
        ("Bugun 15-aprel", "Bugun ўн беш инчи aprel", "Today is April 15th"),
        ("2026-yil 3-iyun", "икки минг йигирма олти-yil уч инчи iyun", "June 3rd, 2026"),
    ]
    
    print("Ordinal number tests:\n")
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = convert_numbers_in_text(input_text)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {description}")
        print(f"   Input:    {input_text}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}\n")
    
    print(f"{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


def test_acronyms():
    """Test all-caps acronym spelling."""
    print("Testing Acronyms (All-Caps Words):\n")
    
    test_cases = [
        ("USA", "у-эс-а", "Latin acronym"),
        ("NATO", "эн-а-те-о", "Latin acronym"),
        ("НАТО", "эн-а-те-о", "Cyrillic acronym"),
        ("СССР", "эс-эс-эс-эр", "Cyrillic acronym"),
        ("Men USA da yashayman", "Men у-эс-а da yashayman", "Acronym in sentence"),
        ("O'zbekiston va NATO", "O'zbekiston va эн-а-те-о", "Mixed text"),
        ("API orqali", "а-пе-и orqali", "Technical acronym"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        # Test individual acronym spelling
        if len(input_text.split()) == 1:
            result = spell_out_acronym(input_text)
        else:
            result = process_acronyms_in_text(input_text)
        
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {description}")
        print(f"   Input:    {input_text}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}\n")
    
    print(f"{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


def test_combined():
    """Test ordinals and acronyms together."""
    print("Testing Combined (Ordinals + Acronyms):\n")
    
    test_cases = [
        "9-yanvar kuni USA prezidenti",
        "NATO va BMT 1-may",
        "API versiya 2",
        "15-aprel COVID-19",
    ]
    
    for text in test_cases:
        # Process acronyms first, then numbers
        result1 = process_acronyms_in_text(text)
        result2 = convert_numbers_in_text(result1)
        
        print(f"Input:  {text}")
        print(f"Step 1: {result1} (acronyms processed)")
        print(f"Step 2: {result2} (numbers processed)\n")


if __name__ == "__main__":
    ordinal_success = test_ordinal_numbers()
    acronym_success = test_acronyms()
    
    print()
    test_combined()
    
    if ordinal_success and acronym_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed")
