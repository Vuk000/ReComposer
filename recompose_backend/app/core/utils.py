# --- Utility Functions ---
"""
Utility functions for common operations.
"""

import re
import asyncio
from typing import Optional, Callable, Any
from openai import OpenAIError, APIError, APITimeoutError, APIConnectionError
import logging

logger = logging.getLogger(__name__)


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


async def retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of func call
        
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except (APIError, APITimeoutError, APIConnectionError) as e:
            last_exception = e
            
            # Don't retry on certain error types
            if isinstance(e, APIError) and e.status_code:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.status_code < 500:
                    raise
            
            if attempt < max_retries:
                logger.warning(
                    f"OpenAI API call failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * exponential_base, max_delay)
            else:
                logger.error(f"OpenAI API call failed after {max_retries + 1} attempts: {str(e)}")
        except Exception as e:
            # Don't retry on unexpected exceptions
            logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
            raise
    
    # If we get here, all retries failed
    raise last_exception

