"""
Simple in-memory cache for TTS audio.
Caches generated audio to save on API costs for repeated text.
"""

import asyncio
import hashlib
from typing import Optional, Dict
from .logger import get_logger

logger = get_logger(__name__)


class AudioCache:
    """Simple LRU-style cache for audio bytes."""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cached items
        """
        self.max_size = max_size
        self.cache: Dict[str, bytes] = {}
        self.access_order: list[str] = []
        self.lock = asyncio.Lock()
        
        logger.info(f"Audio cache initialized with max_size={max_size}")
    
    def _get_hash(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    async def get(self, text: str) -> Optional[bytes]:
        """
        Get cached audio for text.
        
        Args:
            text: Text to look up
        
        Returns:
            Audio bytes if cached, None otherwise
        """
        async with self.lock:
            text_hash = self._get_hash(text)
            
            if text_hash in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(text_hash)
                self.access_order.append(text_hash)
                
                logger.debug(f"Cache hit for text hash: {text_hash[:8]}...")
                return self.cache[text_hash]
            
            logger.debug(f"Cache miss for text hash: {text_hash[:8]}...")
            return None
    
    async def set(self, text: str, audio_bytes: bytes) -> None:
        """
        Cache audio for text.
        
        Args:
            text: Original text
            audio_bytes: Generated audio bytes
        """
        async with self.lock:
            text_hash = self._get_hash(text)
            
            # If cache is full, evict least recently used
            if len(self.cache) >= self.max_size and text_hash not in self.cache:
                evicted_hash = self.access_order.pop(0)
                del self.cache[evicted_hash]
                logger.debug(f"Evicted cache entry: {evicted_hash[:8]}...")
            
            # Add to cache
            self.cache[text_hash] = audio_bytes
            
            # Update access order
            if text_hash in self.access_order:
                self.access_order.remove(text_hash)
            self.access_order.append(text_hash)
            
            logger.debug(f"Cached audio for text hash: {text_hash[:8]}...")
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self.lock:
            self.cache.clear()
            self.access_order.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "usage_percent": (len(self.cache) / self.max_size) * 100
        }


# Global cache instance
_audio_cache: Optional[AudioCache] = None


def get_audio_cache() -> AudioCache:
    """Get or create the global audio cache instance."""
    global _audio_cache
    if _audio_cache is None:
        _audio_cache = AudioCache(max_size=100)
    return _audio_cache
