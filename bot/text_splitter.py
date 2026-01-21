"""
Text splitter for handling long messages.
Splits text into chunks at sentence boundaries for better TTS quality.
Minimum chunk size: 2000 characters
Maximum chunk size: 3000 characters
"""

import re
from typing import List
from .logger import get_logger

logger = get_logger(__name__)


def split_text(text: str, max_length: int = 3000) -> List[str]:
    """
    Split text into chunks at sentence boundaries.
    Minimum chunk size is 2000 characters to preserve context.
    
    Args:
        text: Text to split
        max_length: Maximum characters per chunk (default 3000, minimum 2000)
    
    Returns:
        List of text chunks
    """
    # Ensure minimum chunk size of 2000
    if max_length < 2000:
        max_length = 2000
    
    # Handle empty or whitespace-only text
    if not text or not text.strip():
        return []
    
    # If text is short enough, return as-is
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentence boundaries (., !, ?)
    # This regex matches sentence-ending punctuation followed by space or end of string
    sentences = re.split(r'([.!?]+\s+)', text)
    
    # Reconstruct sentences with their punctuation
    reconstructed_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            reconstructed_sentences.append(sentences[i] + sentences[i + 1])
        else:
            reconstructed_sentences.append(sentences[i])
    
    # Handle last sentence if it doesn't end with punctuation
    if len(sentences) % 2 != 0:
        reconstructed_sentences.append(sentences[-1])
    
    # Group sentences into chunks with minimum 2000 chars
    for sentence in reconstructed_sentences:
        # If single sentence is too long, split by words
        if len(sentence) > max_length:
            word_chunks = _split_by_words(sentence, max_length)
            chunks.extend(word_chunks)
            current_chunk = ""
            continue
        
        # If adding this sentence would exceed max limit
        if len(current_chunk) + len(sentence) > max_length:
            # Only create new chunk if current one meets minimum 2000 chars
            if current_chunk and len(current_chunk) >= 2000:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Keep adding to meet minimum size
                current_chunk += sentence
        else:
            current_chunk += sentence
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Remove empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]
    
    logger.info(f"Split text into {len(chunks)} chunks (min 2000 chars each)")
    return chunks


def _split_by_words(text: str, max_length: int) -> List[str]:
    """
    Split text by word boundaries when sentence is too long.
    
    Args:
        text: Text to split
        max_length: Maximum characters per chunk
    
    Returns:
        List of text chunks
    """
    chunks = []
    words = text.split()
    current_chunk = ""
    
    for word in words:
        # If single word is longer than max_length, split it forcefully
        if len(word) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # Split long word into character chunks
            for i in range(0, len(word), max_length):
                chunks.append(word[i:i + max_length])
            continue
        
        # If adding this word would exceed limit, start new chunk
        if len(current_chunk) + len(word) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
