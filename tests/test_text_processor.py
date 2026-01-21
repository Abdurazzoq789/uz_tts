"""
Unit tests for text_processor module.
Tests hashtag removal, script detection, and text validation.
"""

import pytest
from bot.text_processor import (
    remove_hashtag,
    detect_script,
    validate_text,
    process_text
)


class TestRemoveHashtag:
    """Test hashtag removal functionality."""
    
    def test_remove_simple_hashtag(self):
        """Test removing simple #audio hashtag."""
        text = "Salom dunyo! #audio"
        result = remove_hashtag(text, "#audio")
        assert result == "Salom dunyo!"
    
    def test_remove_hashtag_case_insensitive(self):
        """Test case-insensitive hashtag removal."""
        text = "Test message #AUDIO"
        result = remove_hashtag(text, "#audio")
        assert result == "Test message"
    
    def test_remove_hashtag_multiple_occurrences(self):
        """Test removing multiple hashtags."""
        text = "#audio Salom #audio dunyo #audio"
        result = remove_hashtag(text, "#audio")
        assert result == "Salom dunyo"
    
    def test_remove_hashtag_with_extra_whitespace(self):
        """Test whitespace normalization."""
        text = "Salom    dunyo!   #audio   "
        result = remove_hashtag(text, "#audio")
        assert result == "Salom dunyo!"
    
    def test_preserve_other_hashtags(self):
        """Test that other hashtags are preserved."""
        text = "Salom #uzbekistan #audio #tashkent"
        result = remove_hashtag(text, "#audio")
        assert result == "Salom #uzbekistan #tashkent"


class TestDetectScript:
    """Test script detection (Latin vs Cyrillic)."""
    
    def test_detect_latin_script(self):
        """Test detection of Latin script."""
        text = "Salom dunyo! Bu test."
        result = detect_script(text)
        assert result == "Latin"
    
    def test_detect_cyrillic_script(self):
        """Test detection of Cyrillic script."""
        text = "Салом дунё! Бу тест."
        result = detect_script(text)
        assert result == "Cyrillic"
    
    def test_detect_mixed_script_cyrillic_dominant(self):
        """Test mixed script with Cyrillic dominant."""
        # Note: This is a borderline case - "Салом world дунё test" 
        # has 8 Cyrillic chars vs 9 Latin chars, so Latin wins
        # This is acceptable for logging purposes
        text = "Салом мир дунё тест world"  # More Cyrillic now
        result = detect_script(text)
        assert result == "Cyrillic"
    
    def test_detect_mixed_script_latin_dominant(self):
        """Test mixed script with Latin dominant."""
        text = "Salom мир dunyo тест hello"
        result = detect_script(text)
        assert result == "Latin"
    
    def test_detect_unknown_script(self):
        """Test detection of unknown/no script."""
        text = "123 456 !@# $%^"
        result = detect_script(text)
        assert result == "Unknown"


class TestValidateText:
    """Test text validation."""
    
    def test_validate_normal_text(self):
        """Test validation of normal text."""
        text = "Salom dunyo!"
        assert validate_text(text) is True
    
    def test_validate_empty_string(self):
        """Test validation of empty string."""
        text = ""
        assert validate_text(text) is False
    
    def test_validate_whitespace_only(self):
        """Test validation of whitespace-only string."""
        text = "   \n\t   "
        assert validate_text(text) is False
    
    def test_validate_numbers_only(self):
        """Test validation of numbers-only text."""
        text = "123456789"
        assert validate_text(text) is False
    
    def test_validate_text_with_letters(self):
        """Test validation of text with at least one letter."""
        text = "Test 123"
        assert validate_text(text) is True


class TestProcessText:
    """Test complete text processing pipeline."""
    
    def test_process_valid_text_latin(self):
        """Test processing valid Latin text."""
        text = "Salom dunyo! #audio"
        result = process_text(text, "#audio")
        assert result == "Salom dunyo!"
    
    def test_process_valid_text_cyrillic(self):
        """Test processing valid Cyrillic text."""
        text = "Салом дунё! #audio"
        result = process_text(text, "#audio")
        assert result == "Салом дунё!"
    
    def test_process_text_empty_after_removal(self):
        """Test processing text that becomes empty after hashtag removal."""
        text = "#audio"
        result = process_text(text, "#audio")
        assert result is None
    
    def test_process_text_with_whitespace(self):
        """Test processing text with extra whitespace."""
        text = "  Salom   dunyo!  #audio  "
        result = process_text(text, "#audio")
        assert result == "Salom dunyo!"
    
    def test_process_text_preserves_other_hashtags(self):
        """Test that other hashtags are preserved."""
        text = "Salom #uzbekistan #audio"
        result = process_text(text, "#audio")
        assert result == "Salom #uzbekistan"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
