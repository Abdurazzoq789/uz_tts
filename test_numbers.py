"""
Test number conversion for Uzbek TTS.
"""

from bot.numbers import number_to_uzbek_words, convert_numbers_in_text


def test_number_conversion():
    """Test Uzbek number-to-word conversion."""
    print("\n" + "="*60)
    print("Testing Uzbek Number-to-Word Conversion")
    print("="*60 + "\n")
    
    test_cases = [
        (0, "нол"),
        (1, "бир"),
        (5, "беш"),
        (10, "ўн"),
        (15, "ўн беш"),
        (25, "йигирма беш"),
        (42, "қирқ икки"),
        (100, "юз"),
        (101, "юз бир"),
        (250, "икки юз эллик"),
        (1000, "минг"),
        (2023, "икки минг йигирма уч"),
        (10000, "ўн минг"),
        (1000000, "бир миллион"),
    ]
    
    print("Individual number tests:\n")
    passed = 0
    failed = 0
    
    for num, expected in test_cases:
        result = number_to_uzbek_words(num)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {str(num):10} → {result:30} (expected: {expected})")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


def test_text_conversion():
    """Test number conversion in full text."""
    print("Testing numbers in text:\n")
    
    test_cases = [
        "Men 25 yoshdaman",
        "Bugun 15-yanvar, 2026-yil",
        "Narx: 100000 so'm",
        "Telefon: 998",
        "Sana: 21.01.2026",
    ]
    
    for text in test_cases:
        result = convert_numbers_in_text(text)
        print(f"Input:  {text}")
        print(f"Output: {result}\n")


if __name__ == "__main__":
    success = test_number_conversion()
    print()
    test_text_conversion()
    
    if success:
        print("\n🎉 Number conversion tests passed!")
    else:
        print("\n⚠️  Some tests failed")
