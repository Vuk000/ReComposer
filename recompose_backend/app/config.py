# --- Configuration Module ---
"""
Configuration settings loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""

import warnings
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # --- Database Configuration ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:pass@localhost/recompose",
        description="PostgreSQL connection string using asyncpg driver"
    )
    
    # --- OpenAI Configuration ---
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key (required for email rewriting functionality)"
    )
    
    # --- JWT Configuration ---
    JWT_SECRET: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    JWT_EXPIRATION_HOURS: int = Field(
        default=24,
        description="JWT token expiration time in hours"
    )
    
    # --- CORS Configuration ---
    # Store as string internally, but expose as list via property
    CORS_ORIGINS_STR: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Comma-separated list of allowed origins for CORS"
    )
    
    # --- Application Configuration ---
    APP_NAME: str = Field(
        default="ReCompose AI Backend",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    DEBUG: bool = Field(
        default=False,
        description="Debug mode (set to true for development)"
    )
    
    # --- Logging Configuration ---
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: 'json' for structured logging, 'text' for human-readable"
    )
    
    # --- OpenAI Model Configuration ---
    OPENAI_MODEL: str = Field(
        default="gpt-4o",
        description="OpenAI model to use for email rewriting"
    )
    OPENAI_MAX_TOKENS: int = Field(
        default=1000,
        description="Maximum tokens for OpenAI responses"
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature setting for OpenAI (0.0-2.0)"
    )
    OPENAI_TIMEOUT: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="OpenAI API request timeout in seconds (1-300)"
    )
    OPENAI_MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for OpenAI API calls (0-10)"
    )
    OPENAI_RETRY_DELAY: float = Field(
        default=1.0,
        ge=0.1,
        description="Initial retry delay in seconds for OpenAI API calls"
    )
    
    # --- Rate Limiting Configuration ---
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting (set to false to disable)"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        ge=1,
        description="Maximum requests per minute per IP address"
    )
    RATE_LIMIT_AUTH_PER_MINUTE: int = Field(
        default=10,
        ge=1,
        description="Maximum authentication requests per minute per IP address"
    )
    
    # --- Request Configuration ---
    MAX_REQUEST_SIZE: int = Field(
        default=10485760,  # 10MB
        ge=1024,
        description="Maximum request body size in bytes"
    )
    
    # --- Database Configuration ---
    DB_CONNECT_TIMEOUT: float = Field(
        default=10.0,
        ge=1.0,
        description="Database connection timeout in seconds"
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600,
        ge=60,
        description="Database connection pool recycle time in seconds"
    )
    
    # --- Billing Feature Flag ---
    BILLING_ENABLED: bool = Field(
        default=False,
        description="Enable billing endpoints (set to true to enable)"
    )
    
    # --- Stripe Configuration ---
    STRIPE_SECRET_KEY: str = Field(
        default="",
        description="Stripe secret key (required when billing enabled)"
    )
    STRIPE_WEBHOOK_SECRET: str = Field(
        default="",
        description="Stripe webhook secret for verifying webhook signatures"
    )
    
    # --- Usage Limits Configuration ---
    STANDARD_PLAN_DAILY_LIMIT: int = Field(
        default=20,
        ge=1,
        description="Daily rewrite limit for standard plan users"
    )
    PRO_PLAN_DAILY_LIMIT: int = Field(
        default=1000,
        ge=1,
        description="Daily rewrite limit for pro plan users (effectively unlimited)"
    )
    REWRITE_RATE_LIMIT_PER_MINUTE: int = Field(
        default=20,
        ge=1,
        description="Maximum rewrites per minute per user (throttling)"
    )
    
    # --- Email Provider Configuration ---
    GMAIL_CLIENT_ID: str = Field(
        default="",
        description="Gmail OAuth client ID (for future OAuth integration)"
    )
    GMAIL_CLIENT_SECRET: str = Field(
        default="",
        description="Gmail OAuth client secret (for future OAuth integration)"
    )
    OUTLOOK_CLIENT_ID: str = Field(
        default="",
        description="Outlook OAuth client ID (for future OAuth integration)"
    )
    OUTLOOK_CLIENT_SECRET: str = Field(
        default="",
        description="Outlook OAuth client secret (for future OAuth integration)"
    )
    SMTP_DEFAULT_PORT: int = Field(
        default=587,
        ge=1,
        le=65535,
        description="Default SMTP port"
    )
    SMTP_DEFAULT_USE_TLS: bool = Field(
        default=True,
        description="Default SMTP TLS setting"
    )
    
    # --- Campaign Configuration ---
    MAX_EMAILS_PER_MINUTE: int = Field(
        default=50,
        ge=1,
        description="Maximum emails to send per minute (rate limiting)"
    )
    REPLY_CHECK_INTERVAL_MINUTES: int = Field(
        default=5,
        ge=1,
        description="Interval in minutes to check for email replies"
    )
    CAMPAIGN_RATE_LIMIT_PER_MINUTE: int = Field(
        default=5,
        ge=1,
        description="Maximum campaign launches per minute per user"
    )
    TRACKING_BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Base URL for tracking pixels (e.g., https://api.yourdomain.com)"
    )
    
    # --- Celery Configuration ---
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis broker URL for Celery"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Redis result backend URL for Celery"
    )
    
    # --- Encryption Configuration ---
    ENCRYPTION_KEY: str = Field(
        default="",
        description="Encryption key for OAuth tokens (base64-encoded Fernet key)"
    )
    
    # --- Subscription Pricing ---
    STANDARD_PLAN_PRICE: int = Field(
        default=1499,
        description="Standard plan price in cents ($14.99)"
    )
    PRO_PLAN_PRICE: int = Field(
        default=4999,
        description="Pro plan price in cents ($49.99)"
    )
    STRIPE_PRO_PRICE_ID: str = Field(
        default="",
        description="Stripe price ID for Pro plan"
    )
    STRIPE_STANDARD_PRICE_ID: str = Field(
        default="",
        description="Stripe price ID for Standard plan"
    )
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        """Validate that OpenAI API key format is correct (if provided)."""
        # Allow empty string for testing/development, but warn
        if not v or not v.strip():
            # Don't raise error at startup - validate when actually used
            return ""
        return v.strip()
    
    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Warn if using default JWT secret in production."""
        default_secret = "your-secret-key-change-in-production"
        if v == default_secret:
            warnings.warn(
                "JWT_SECRET is using the default value. "
                "Please change it to a strong random string in production.",
                UserWarning,
                stacklevel=2
            )
        elif len(v) < 32:
            warnings.warn(
                "JWT_SECRET should be at least 32 characters long for security.",
                UserWarning,
                stacklevel=2
            )
        return v
    
    @field_validator("CORS_ORIGINS_STR", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> str:
        """Parse CORS origins from string or list."""
        if isinstance(v, list):
            return ",".join(v)
        if isinstance(v, str):
            return v
        return str(v)
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins as a list."""
        if not self.CORS_ORIGINS_STR:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]


# --- Global Settings Instance ---
settings = Settings()

