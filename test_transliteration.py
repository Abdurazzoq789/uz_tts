"""
Test transliteration functionality.
Verifies Latin to Cyrillic conversion for Uzbek.
"""

from bot.transliterate import latin_to_cyrillic, transliterate_if_latin


def test_basic_transliteration():
    """Test basic Latin to Cyrillic conversion."""
    print("\n" + "="*60)
    print("Testing Uzbek Latin → Cyrillic Transliteration")
    print("="*60 + "\n")
    
    test_cases = [
        # (Latin, Expected Cyrillic)
        ("Salom", "Салом"),
        ("dunyo", "дунё"),
        ("o'zbek", "ўзбек"),
        ("Salom dunyo!", "Салом дунё!"),
        ("O'zbekiston", "Ўзбекистон"),
        ("Toshkent", "Тошкент"),
        ("Samarqand", "Самарқанд"),
        ("Buxoro", "Бухоро"),
        ("Yaxshi", "Яхши"),
        ("Rahmat", "Раҳмат"),
        ("Sog'lom bo'ling", "Соғлом бўлинг"),
        ("Xayr", "Хайр"),
        ("Cho'ponlar", "Чўпонлар"),
        ("Ish", "Иш"),
        ("Mening ismim Ali", "Менинг исмим Али"),
    ]
    
    print("Testing individual conversions:\n")
    passed = 0
    failed = 0
    
    for latin, expected in test_cases:
        result = latin_to_cyrillic(latin)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {latin:25} → {result:25} (expected: {expected})")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


def test_auto_detection():
    """Test automatic Latin/Cyrillic detection."""
    print("Testing automatic script detection:\n")
    
    test_texts = [
        ("Salom dunyo!", True, "Should detect as Latin"),
        ("Салом дунё!", False, "Should detect as Cyrillic"),
        ("Hello world test", True, "Should detect as Latin"),
        ("Бу тест хабари", False, "Should detect as Cyrillic"),
    ]
    
    for text, should_be_latin, description in test_texts:
        result, was_latin = transliterate_if_latin(text)
        status = "✅" if was_latin == should_be_latin else "❌"
        script = "Latin" if was_latin else "Cyrillic"
        
        print(f"{status} {description}")
        print(f"   Input:  {text}")
        print(f"   Detected: {script}")
        print(f"   Output: {result}\n")


if __name__ == "__main__":
    # Test transliteration
    success = test_basic_transliteration()
    
    # Test auto-detection
    test_auto_detection()
    
    if success:
        print("\n🎉 All transliteration tests passed!")
    else:
        print("\n⚠️  Some tests failed - check output above")
