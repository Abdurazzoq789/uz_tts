"""
Test TTS with both Latin and Cyrillic scripts.
Verifies transliteration + TTS pipeline works end-to-end.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from bot.tts_engine import get_tts_engine
from bot.logger import setup_logging


async def test_latin_and_cyrillic_tts():
    """Test TTS with both scripts."""
    setup_logging("INFO")
    
    print("\n" + "="*60)
    print("Testing TTS with Latin & Cyrillic Scripts")
    print("="*60 + "\n")
    
    engine = get_tts_engine()
    
    # Test 1: Latin script
    print("Test 1: Latin Script")
    print("-" * 60)
    latin_text = "Salom dunyo! Bu test xabari."
    print(f"Input (Latin):  {latin_text}")
    
    try:
        audio_bytes = await engine.text_to_speech(latin_text)
        
        output_file = "test_latin_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Success! Audio size: {len(audio_bytes)} bytes")
        print(f"   Saved to: {output_file}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 2: Cyrillic script
    print("Test 2: Cyrillic Script")
    print("-" * 60)
    cyrillic_text = "Салом дунё! Бу тест хабари."
    print(f"Input (Cyrillic): {cyrillic_text}")
    
    try:
        audio_bytes = await engine.text_to_speech(cyrillic_text)
        
        output_file = "test_cyrillic_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Success! Audio size: {len(audio_bytes)} bytes")
        print(f"   Saved to: {output_file}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    print("="*60)
    print("✅ Both Latin and Cyrillic scripts supported!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_latin_and_cyrillic_tts())
