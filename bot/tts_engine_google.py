"""
Google Cloud Text-to-Speech integration.
Converts Uzbek text (Latin and Cyrillic) to speech audio.
"""

import asyncio
from typing import Optional
from google.cloud import texttospeech
from .config import get_config
from .exceptions import TTSError
from .logger import get_logger
import time

logger = get_logger(__name__)


class TTSEngine:
    """Google Cloud TTS wrapper for Uzbek language."""
    
    def __init__(self):
        """Initialize the TTS client."""
        self.config = get_config()
        self.client = texttospeech.TextToSpeechClient()
        
        # Configure voice settings
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="uz-UZ",
            name=self.config.voice_name
        )
        
        # Configure audio settings
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        logger.info(f"TTS Engine initialized with voice: {self.config.voice_name}")
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Uzbek text in Latin or Cyrillic script
        
        Returns:
            Audio bytes in MP3 format
        
        Raises:
            TTSError: If TTS generation fails
        """
        start_time = time.time()
        
        try:
            # Run TTS in executor to avoid blocking
            loop = asyncio.get_event_loop()
            audio_bytes = await loop.run_in_executor(
                None,
                self._generate_speech,
                text
            )
            
            elapsed = time.time() - start_time
            logger.info(
                f"Generated audio for {len(text)} chars in {elapsed:.2f}s, "
                f"audio size: {len(audio_bytes)} bytes"
            )
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}", exc_info=True)
            raise TTSError(f"Failed to generate speech: {e}")
    
    def _generate_speech(self, text: str) -> bytes:
        """
        Synchronous TTS generation (called in executor).
        
        Args:
            text: Text to convert
        
        Returns:
            Audio bytes
        """
        # Create synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Generate speech
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )
        
        return response.audio_content


# Global TTS engine instance
_tts_engine: Optional[TTSEngine] = None


def get_tts_engine() -> TTSEngine:
    """Get or create the global TTS engine instance."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
