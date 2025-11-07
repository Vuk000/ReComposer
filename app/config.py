# --- Configuration Module ---
"""
Configuration settings loaded from environment variables.
Uses python-dotenv to load .env file.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # --- Database Configuration ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:pass@localhost/recompose"
    )
    
    # --- OpenAI Configuration ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # --- JWT Configuration ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # --- CORS Configuration ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        # Add your Vercel deployment URL here, e.g.:
        # "https://your-app.vercel.app",
    ]
    
    # --- Application Configuration ---
    APP_NAME: str = "ReCompose AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # --- OpenAI Model Configuration ---
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))


# --- Global Settings Instance ---
settings = Settings()

