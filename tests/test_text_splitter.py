"""
Unit tests for text_splitter module.
Tests text splitting at sentence boundaries.
"""

import pytest
from bot.text_splitter import split_text


class TestSplitText:
    """Test text splitting functionality."""
    
    def test_short_text_no_split(self):
        """Test that short text is not split."""
        text = "Salom dunyo! Bu qisqa matn."
        result = split_text(text, max_length=1000)
        assert len(result) == 1
        assert result[0] == text
    
    def test_exact_max_length(self):
        """Test text exactly at max length."""
        text = "a" * 100
        result = split_text(text, max_length=100)
        assert len(result) == 1
        assert result[0] == text
    
    def test_long_text_split_by_sentences(self):
        """Test splitting long text at sentence boundaries."""
        text = "Birinchi jumla. " * 200 + "Ikkinchi jumla. " * 200
        result = split_text(text, max_length=500)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 500
    
    def test_split_preserves_content(self):
        """Test that splitting preserves all content."""
        text = "Salom dunyo! " * 500
        result = split_text(text, max_length=1000)
        rejoined = " ".join(result)
        # Normalize whitespace for comparison
        assert rejoined.replace("  ", " ").strip() == text.strip()
    
    def test_split_with_punctuation(self):
        """Test splitting with various punctuation."""
        text = "Birinchi? Ikkinchi! Uchinchi. " * 200
        result = split_text(text, max_length=500)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 500
    
    def test_split_no_punctuation(self):
        """Test splitting text without sentence punctuation."""
        text = "so'z " * 1000  # 1000 words without punctuation
        result = split_text(text, max_length=500)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 500
    
    def test_single_very_long_word(self):
        """Test splitting a single very long word."""
        text = "a" * 5000
        result = split_text(text, max_length=1000)
        assert len(result) == 5
        for chunk in result:
            assert len(chunk) <= 1000
    
    def test_empty_text(self):
        """Test splitting empty text."""
        text = ""
        result = split_text(text, max_length=100)
        assert len(result) == 0
    
    def test_whitespace_only(self):
        """Test splitting whitespace-only text."""
        text = "   \n\t   "
        result = split_text(text, max_length=100)
        assert len(result) == 0
    
    def test_chunk_boundaries_respect_sentences(self):
        """Test that chunks don't split mid-sentence when possible."""
        sentences = [
            "Bu birinchi jumla.",
            "Bu ikkinchi jumla.",
            "Bu uchinchi jumla.",
            "Bu to'rtinchi jumla."
        ]
        text = " ".join(sentences)
        
        result = split_text(text, max_length=50)
        
        # Each chunk should end with sentence-ending punctuation (when possible)
        for chunk in result:
            if len(chunk) < 50:  # If not at max length, should be complete sentence
                assert chunk.rstrip()[-1] in ".!?" or chunk == result[-1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
