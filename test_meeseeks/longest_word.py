"""Module for finding the longest word in a sentence."""


def find_longest_word(sentence: str) -> str:
    """
    Find and return the longest word in a sentence.
    
    Args:
        sentence: A string containing one or more words.
        
    Returns:
        The longest word in the sentence. If multiple words have the same
        maximum length, returns the first one encountered.
        
    Raises:
        ValueError: If the sentence is empty or contains no valid words.
    """
    if not sentence or not sentence.strip():
        raise ValueError("Sentence cannot be empty")
    
    # Split on whitespace and filter out empty strings
    words = [word for word in sentence.split() if word]
    
    if not words:
        raise ValueError("Sentence must contain at least one word")
    
    # Find the longest word (first one if there's a tie)
    return max(words, key=len)
