# --- User Settings Router ---
"""
User settings and preferences endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/user", tags=["user-settings"])

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class UserSettingsUpdate(BaseModel):
    """User settings update model."""
    default_tone: Optional[str] = Field(None, description="Default tone preference (friendly, professional, persuasive)")
    style_learning_enabled: Optional[bool] = Field(None, description="Enable style learning from user rewrites")
    email_notifications: Optional[bool] = Field(None, description="Enable email notifications")
    marketing_emails: Optional[bool] = Field(None, description="Enable marketing emails")


class UserSettingsResponse(BaseModel):
    """User settings response model."""
    model_config = ConfigDict(from_attributes=True)
    
    default_tone: Optional[str] = None
    style_learning_enabled: bool = False
    email_notifications: bool = True
    marketing_emails: bool = False


class UserProfileResponse(BaseModel):
    """User profile response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    subscription_plan: str
    subscription_status: str
    created_at: str


# --- Get User Settings Endpoint ---
@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user settings and preferences.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User settings
    """
    # For now, return default settings
    # In the future, we can add a UserSettings model to store these preferences
    return {
        "default_tone": None,  # Can be stored in user model or separate settings table
        "style_learning_enabled": False,
        "email_notifications": True,
        "marketing_emails": False
    }


# --- Update User Settings Endpoint ---
@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    request: Request,
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user settings and preferences.
    
    Args:
        request: FastAPI request object
        settings_update: Settings to update
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user settings
    """
    # For now, just return the updated settings
    # In the future, we can add a UserSettings model to store these preferences
    updated_settings = {
        "default_tone": settings_update.default_tone,
        "style_learning_enabled": settings_update.style_learning_enabled if settings_update.style_learning_enabled is not None else False,
        "email_notifications": settings_update.email_notifications if settings_update.email_notifications is not None else True,
        "marketing_emails": settings_update.marketing_emails if settings_update.marketing_emails is not None else False
    }
    
    logger.info(
        f"User {current_user.id} updated settings",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return updated_settings


# --- Get User Profile Endpoint ---
@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        
    Returns:
        User profile information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "subscription_plan": current_user.subscription_plan,
        "subscription_status": current_user.subscription_status,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

