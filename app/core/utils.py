# --- Utility Functions ---
"""
Utility functions for common operations.
"""

import re
from typing import Optional


def count_words(text: str) -> int:
    """
    Count words in a text string.
    
    Args:
        text: Input text string
        
    Returns:
        Word count as integer
    """
    if not text or not text.strip():
        return 0
    # Split by whitespace and filter out empty strings
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def extract_tokens_from_usage(usage: Optional[dict]) -> int:
    """
    Extract total tokens used from OpenAI API usage response.
    
    Args:
        usage: OpenAI usage dictionary
        
    Returns:
        Total tokens used, or 0 if not available
    """
    if not usage:
        return 0
    # OpenAI returns total_tokens, but we'll use it if available
    return usage.get("total_tokens", 0)

