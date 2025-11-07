# --- Billing Router ---
"""
Billing endpoints (placeholder for future Stripe integration).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.routers.auth import get_current_user
from app.models.user import User

# --- Router Setup ---
router = APIRouter(prefix="/billing", tags=["billing"])


# --- Pydantic Models ---
class SubscribeRequest(BaseModel):
    """Subscription request model (placeholder)."""
    plan: str  # e.g., "basic", "pro", "enterprise"


class SubscribeResponse(BaseModel):
    """Subscription response model (placeholder)."""
    message: str
    plan: str
    status: str = "pending"


# --- Subscribe Endpoint (Placeholder) ---
@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Subscribe to a plan (placeholder for future Stripe integration).
    
    TODO: Integrate with Stripe API to:
    1. Create customer if not exists
    2. Create subscription
    3. Handle webhooks for payment events
    4. Update user subscription status in database
    
    Args:
        request: Subscription request with plan name
        current_user: Current authenticated user
        
    Returns:
        Subscription confirmation message
    """
    valid_plans = ["basic", "pro", "enterprise"]
    
    if request.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan must be one of: {', '.join(valid_plans)}"
        )
    
    # --- Placeholder response ---
    return {
        "message": "Subscription endpoint is a placeholder. Stripe integration pending.",
        "plan": request.plan,
        "status": "pending"
    }

