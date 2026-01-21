"""
Quick test script for MMS TTS Engine.
Tests the Facebook MMS VITS model without needing full bot setup.
"""

import asyncio
import sys
import os

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

from bot.tts_engine import get_tts_engine
from bot.logger import setup_logging


async def test_mms_tts():
    """Test MMS TTS with sample Uzbek text."""
    setup_logging("INFO")
    
    print("\n" + "="*60)
    print("Testing Facebook MMS VITS TTS Engine")
    print("="*60 + "\n")
    
    # Initialize engine
    print("Initializing TTS engine...")
    engine = get_tts_engine()
    
    # Test Cyrillic text
    test_text = "Салом дунё! Бу тест."
    print(f"\nTest text (Cyrillic): {test_text}")
    print("Generating audio... (this may take 10-15 seconds on first run)")
    
    try:
        audio_bytes = await engine.text_to_speech(test_text)
        
        # Save to file
        output_file = "test_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"\n✅ Success!")
        print(f"   Audio generated: {len(audio_bytes)} bytes")
        print(f"   Saved to: {output_file}")
        print("\nYou can play the file to verify the audio quality.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mms_tts())
