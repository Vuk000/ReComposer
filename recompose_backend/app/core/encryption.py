# --- Encryption Module ---
"""
Encryption utilities for securing OAuth tokens and sensitive data.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _get_encryption_key() -> bytes:
    """
    Get or generate encryption key from settings.
    
    Uses ENCRYPTION_KEY from settings. If not set, generates a key
    (not recommended for production).
    
    Returns:
        Encryption key as bytes
    """
    encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
    
    if not encryption_key:
        logger.warning("ENCRYPTION_KEY not set. Generating a key (not recommended for production)")
        # Generate a key (for development only)
        key = Fernet.generate_key()
        return key
    
    # If key is provided as string, convert to bytes
    if isinstance(encryption_key, str):
        # If it's a base64-encoded key, decode it
        try:
            return base64.urlsafe_b64decode(encryption_key.encode())
        except Exception:
            # If not base64, derive a key from the string using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'recompose_salt',  # In production, use a random salt stored securely
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
    
    return encryption_key


def encrypt_token(token: str) -> str:
    """
    Encrypt a token string.
    
    Args:
        token: Plain text token to encrypt
        
    Returns:
        Encrypted token as base64 string
    """
    if not token:
        return ""
    
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Error encrypting token: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to encrypt token: {str(e)}")


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt an encrypted token string.
    
    Args:
        encrypted_token: Encrypted token as base64 string
        
    Returns:
        Decrypted token as plain text
    """
    if not encrypted_token:
        return ""
    
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting token: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to decrypt token: {str(e)}")

