# --- Status Router ---
"""
Status endpoint to check what features are configured and available.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/api/status", tags=["status"])


class StatusResponse(BaseModel):
    """Status response model showing what's configured."""
    ai_provider: str  # "openai", "anthropic", "none"
    billing_enabled: bool
    stripe_configured: bool
    rewrite_available: bool
    billing_available: bool


@router.get("", response_model=StatusResponse)
async def get_status():
    """
    Get status of configured services.
    Returns what features are available based on environment configuration.
    """
    # Check AI provider
    has_openai = bool(settings.OPENAI_API_KEY)
    has_anthropic = bool(settings.ANTHROPIC_API_KEY)
    
    if has_anthropic and settings.USE_ANTHROPIC:
        ai_provider = "anthropic"
    elif has_openai:
        ai_provider = "openai"
    else:
        ai_provider = "none"
    
    # Check billing
    billing_enabled = settings.BILLING_ENABLED
    stripe_configured = bool(settings.STRIPE_SECRET_KEY)
    
    return StatusResponse(
        ai_provider=ai_provider,
        billing_enabled=billing_enabled,
        stripe_configured=stripe_configured,
        rewrite_available=ai_provider != "none",
        billing_available=billing_enabled and stripe_configured
    )

