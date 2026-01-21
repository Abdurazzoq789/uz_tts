"""
Test newline pause handling and bot username in audio.
"""

from bot.text_processor import remove_hashtag, process_text


def test_newline_handling():
    """Test that newlines are converted to periods for pauses."""
    print("\n" + "="*60)
    print("Testing Newline → Pause Conversion")
    print("="*60 + "\n")
    
    test_cases = [
        ("Salom\nDunyo #audio", "Salom. Dunyo"),
        ("Line1\nLine2\nLine3 #audio", "Line1. Line2. Line3"),
        ("Text\n\nDouble newline #audio", "Text. Double newline"),
        ("Normal text #audio", "Normal text"),
        ("End\n #audio", "End."),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected in test_cases:
        result = remove_hashtag(input_text, "#audio")
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Input: {repr(input_text[:30])}")
        print(f"   Expected: {repr(expected)}")
        print(f"   Got:      {repr(result)}\n")
    
    print(f"{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


def test_full_processing():
    """Test full text processing with newlines."""
    print("Testing Full Processing:\n")
    
    test_texts = [
        "Salom!\nMen Ali.\nYaxshi ko'rishguncha! #audio",
        "Line 1\n\nLine 2\n\nLine 3 #audio",
        "Title:\nContent here #audio",
    ]
    
    for text in test_texts:
        result = process_text(text, "#audio")
        print(f"Input:  {repr(text)}")
        print(f"Output: {repr(result)}\n")


if __name__ == "__main__":
    success = test_newline_handling()
    print()
    test_full_processing()
    
    if success:
        print("\n🎉 Newline handling tests passed!")
    else:
        print("\n⚠️  Some tests failed")
