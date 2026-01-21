"""
Facebook MMS (Massively Multilingual Speech) TTS Engine for Uzbek.
Uses VITS model from Hugging Face Transformers - completely free and open-source.
"""

import asyncio
import io
import logging
from typing import Optional
import torch
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer
from pydub import AudioSegment

from .config import get_config
from .exceptions import TTSError
from .logger import get_logger
import time

logger = get_logger(__name__)


class MMS_TTSEngine:
    """Facebook MMS VITS TTS wrapper for Uzbek language (Cyrillic script)."""
    
    def __init__(self):
        """Initialize the MMS TTS engine."""
        self.config = get_config()
        self.model: Optional[VitsModel] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model_loaded = False
        
        logger.info("MMS TTS Engine initializing...")
    
    def _load_model(self):
        """Load the MMS VITS model (called on first use)."""
        if self.model_loaded:
            return
        
        logger.info("Loading Facebook MMS VITS model for Uzbek (Cyrillic)...")
        start_time = time.time()
        
        try:
            # Load Cyrillic Uzbek model
            model_name = "facebook/mms-tts-uzb-script_cyrillic"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = VitsModel.from_pretrained(model_name)
            
            # Move to GPU if available (optional)
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("Model loaded on GPU")
            else:
                logger.info("Model loaded on CPU")
            
            self.model_loaded = True
            
            elapsed = time.time() - start_time
            logger.info(f"Model loaded successfully in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load MMS model: {e}", exc_info=True)
            raise TTSError(f"Failed to load MMS TTS model: {e}")
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert Uzbek text to speech audio.
        Automatically detects and converts Latin to Cyrillic if needed.
        
        Args:
            text: Uzbek text in Latin or Cyrillic script
        
        Returns:
            Audio bytes in MP3 format
        
        Raises:
            TTSError: If TTS generation fails
        """
        start_time = time.time()
        
        try:
            # Load model on first use
            if not self.model_loaded:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._load_model)
            
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
            text: Text to convert (Latin or Cyrillic, may contain numbers and acronyms)
        
        Returns:
            Audio bytes in MP3 format
        """
        # Import here to avoid circular dependency
        from .transliterate import transliterate_if_latin
        from .numbers import convert_numbers_in_text
        from .acronyms import process_acronyms_in_text
        
        # Step 1: Process acronyms (spell out all-caps words)
        text_with_acronyms = process_acronyms_in_text(text)
        if text_with_acronyms != text:
            logger.debug(f"Processed acronyms: {text[:50]}... → {text_with_acronyms[:50]}...")
        
        # Step 2: Convert numbers to words (including ordinals)
        text_with_words = convert_numbers_in_text(text_with_acronyms)
        if text_with_words != text_with_acronyms:
            logger.debug(f"Converted numbers: {text_with_acronyms[:50]}... → {text_with_words[:50]}...")
        
        # Step 3: Auto-transliterate Latin to Cyrillic if needed
        cyrillic_text, was_latin = transliterate_if_latin(text_with_words)
        
        if was_latin:
            logger.info(f"Transliterated Latin → Cyrillic: {len(text)} chars")
        
        # Normalize text (lowercase, remove punctuation)
        # MMS models are trained on normalized text
        normalized_text = cyrillic_text.lower().strip()
        
        # Tokenize
        inputs = self.tokenizer(normalized_text, return_tensors="pt")
        
        # Move inputs to same device as model
        if torch.cuda.is_available() and next(self.model.parameters()).is_cuda:
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate waveform
        with torch.no_grad():
            output = self.model(**inputs).waveform
        
        # Move to CPU for processing
        waveform = output.squeeze().cpu().numpy()
        
        # Convert to WAV format in memory
        wav_io = io.BytesIO()
        scipy.io.wavfile.write(
            wav_io,
            rate=16000,  # MMS models output 16kHz audio
            data=waveform
        )
        wav_io.seek(0)
        
        # Convert WAV to MP3 using pydub
        audio = AudioSegment.from_wav(wav_io)
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3", bitrate="192k")
        
        return mp3_io.getvalue()


# Global TTS engine instance
_tts_engine: Optional[MMS_TTSEngine] = None


def get_tts_engine() -> MMS_TTSEngine:
    """Get or create the global TTS engine instance."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = MMS_TTSEngine()
    return _tts_engine
