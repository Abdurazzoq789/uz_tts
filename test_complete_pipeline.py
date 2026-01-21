"""
End-to-end test with numbers and both scripts.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from bot.tts_engine import get_tts_engine
from bot.logger import setup_logging


async def test_full_pipeline():
    """Test complete TTS pipeline with numbers and transliteration."""
    setup_logging("INFO")
    
    print("\n" + "="*60)
    print("Testing Complete TTS Pipeline")
    print("Numbers + Latin/Cyrillic Support")
    print("="*60 + "\n")
    
    engine = get_tts_engine()
    
    test_cases = [
        # (text, description)
        ("Men 25 yoshdaman", "Latin with number"),
        ("Bugun 15-yanvar", "Latin with date"),
        ("Narx: 1000 so'm", "Latin with price"),
        ("Мен 30 ёшдаман", "Cyrillic with number"),
        ("Telefon: 998 90 123 45 67", "Phone number"),
        ("2+2=4", "Math expression"),
        ("Sana: 21.01.2026", "Date with dots"),
    ]
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print("-" * 60)
        print(f"Input: {text}")
        
        try:
            audio_bytes = await engine.text_to_speech(text)
            
            output_file = f"test_case_{i}.mp3"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            
            print(f"✅ Generated: {len(audio_bytes)} bytes → {output_file}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("="*60)
    print("✅ Pipeline test complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
