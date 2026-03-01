"""Tests for the longest_word module."""

import pytest
from longest_word import find_longest_word


class TestFindLongestWord:
    """Test cases for find_longest_word function."""
    
    def test_simple_sentence(self):
        """Test finding longest word in a simple sentence."""
        sentence = "The quick brown fox jumps"
        result = find_longest_word(sentence)
        assert result == "quick" or result == "brown" or result == "jumps"
        # All are 5 letters, should return first encountered ("quick")
        assert result == "quick"
    
    def test_clear_longest_word(self):
        """Test sentence with one clearly longest word."""
        sentence = "I love programming"
        result = find_longest_word(sentence)
        assert result == "programming"
    
    def test_single_word(self):
        """Test with a single word."""
        sentence = "supercalifragilisticexpialidocious"
        result = find_longest_word(sentence)
        assert result == "supercalifragilisticexpialidocious"
    
    def test_multiple_longest_returns_first(self):
        """Test that first longest word is returned when there's a tie."""
        sentence = "cat dog bat rat"
        result = find_longest_word(sentence)
        assert result == "cat"  # All same length, should return first
    
    def test_empty_sentence_raises_error(self):
        """Test that empty sentence raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            find_longest_word("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            find_longest_word("   \t\n  ")
    
    def test_preserves_word_characters(self):
        """Test that punctuation stays with words."""
        sentence = "Hello, world! How are you?"
        result = find_longest_word(sentence)
        assert result == "Hello,"  # 6 chars including comma
