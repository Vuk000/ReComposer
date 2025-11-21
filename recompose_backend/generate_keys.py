#!/usr/bin/env python3
"""
Generate secure keys for production deployment.

This script generates:
- JWT_SECRET: A secure random hex string (64 characters) for JWT token signing
- ENCRYPTION_KEY: A Fernet encryption key (base64-encoded) for OAuth token encryption

Usage:
    python generate_keys.py

Output:
    Prints the keys in .env format that can be copied to your .env file.
"""

import secrets
from cryptography.fernet import Fernet

def generate_jwt_secret() -> str:
    """Generate a secure JWT secret (64 hex characters = 32 bytes)."""
    return secrets.token_hex(32)

def generate_encryption_key() -> str:
    """Generate a Fernet encryption key for OAuth token encryption."""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("=" * 70)
    print("ReCompose AI - Secure Key Generator")
    print("=" * 70)
    print()
    print("Generated secure keys for production deployment:")
    print()
    print(f"JWT_SECRET={generate_jwt_secret()}")
    print(f"ENCRYPTION_KEY={generate_encryption_key()}")
    print()
    print("=" * 70)
    print("IMPORTANT: Copy these values to your .env file.")
    print("Never commit these keys to version control!")
    print("=" * 70)

