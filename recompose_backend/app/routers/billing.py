# --- Billing Router ---
"""
Billing endpoints for Stripe subscription management.
Gated behind BILLING_ENABLED feature flag.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import stripe
import logging
from app.routers.auth import get_current_user
from app.models.user import User
from app.config import settings
from app.db import get_db

# --- Router Setup ---
router = APIRouter(prefix="/billing", tags=["billing"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- Stripe Configuration ---
if settings.BILLING_ENABLED and settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


# --- Pydantic Models ---
class SubscribeRequest(BaseModel):
    """Subscription request model."""
    plan: str  # "standard" ($14.99/month) or "pro" ($49.99/month)
    payment_method_id: Optional[str] = None  # Stripe payment method ID


class SubscribeResponse(BaseModel):
    """Subscription response model."""
    message: str
    plan: str
    status: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None


class SubscriptionStatusResponse(BaseModel):
    """Subscription status response model."""
    plan: str
    status: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None


class CancelResponse(BaseModel):
    """Cancel subscription response model."""
    message: str
    status: str


# --- Helper Functions ---
async def get_or_create_stripe_customer(user: User) -> str:
    """
    Get or create Stripe customer for user.
    
    Args:
        user: User object
        
    Returns:
        Stripe customer ID
    """
    if user.stripe_customer_id:
        # Verify customer still exists in Stripe
        try:
            stripe.Customer.retrieve(user.stripe_customer_id)
            return user.stripe_customer_id
        except stripe.error.InvalidRequestError:
            # Customer doesn't exist, create new one
            pass
    
    # Create new customer
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.id)}
    )
    return customer.id


def get_stripe_price_id(plan: str) -> str:
    """
    Get Stripe price ID for plan.
    
    Args:
        plan: Plan name (standard, pro)
        
    Returns:
        Stripe price ID
    """
    price_map = {
        "standard": settings.STRIPE_STANDARD_PRICE_ID if hasattr(settings, 'STRIPE_STANDARD_PRICE_ID') and settings.STRIPE_STANDARD_PRICE_ID else None,
        "pro": settings.STRIPE_PRO_PRICE_ID if hasattr(settings, 'STRIPE_PRO_PRICE_ID') and settings.STRIPE_PRO_PRICE_ID else None,
    }
    
    price_id = price_map.get(plan)
    if not price_id:
        # Fallback: use plan name (requires Stripe products to be set up)
        raise ValueError(f"Price ID not configured for plan: {plan}")
    
    return price_id


# --- Subscribe Endpoint ---
@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
    request: Request,
    subscribe_request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to a plan using Stripe.
    
    Args:
        request: FastAPI request object
        subscribe_request: Subscription request with plan name
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Subscription confirmation
    """
    # Check if billing is enabled
    if not settings.BILLING_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing endpoints are currently disabled. Set BILLING_ENABLED=true to enable."
        )
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is not configured. Please set STRIPE_SECRET_KEY in your environment."
        )
    
    valid_plans = ["standard", "pro"]
    
    if subscribe_request.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan must be one of: {', '.join(valid_plans)}"
        )
    
    try:
        # Get or create Stripe customer
        customer_id = await get_or_create_stripe_customer(current_user)
        
        # Get price ID for plan
        try:
            price_id = get_stripe_price_id(subscribe_request.plan)
        except ValueError:
            # For MVP, if price IDs aren't configured, we'll create subscription with plan name
            # In production, this should be properly configured
            logger.warning(f"Price ID not configured for plan {subscribe_request.plan}, using plan name")
            # Create a subscription with metadata instead
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"ReCompose AI {subscribe_request.plan.title()} Plan",
                        },
                        "recurring": {
                            "interval": "month",
                        },
                        "unit_amount": settings.STANDARD_PLAN_PRICE if subscribe_request.plan == "standard" else settings.PRO_PLAN_PRICE,
                    },
                }],
                metadata={"user_id": str(current_user.id), "plan": subscribe_request.plan}
            )
        else:
            # Create subscription with price ID
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={"user_id": str(current_user.id), "plan": subscribe_request.plan}
            )
        
        # Update user in database
        current_user.stripe_customer_id = customer_id
        current_user.stripe_subscription_id = subscription.id
        current_user.subscription_plan = subscribe_request.plan
        current_user.subscription_status = subscription.status
        
        try:
            await db.commit()
            await db.refresh(current_user)
        except Exception as db_error:
            # If database commit fails, try to cancel the Stripe subscription to maintain consistency
            logger.error(
                f"Database commit failed after Stripe subscription creation. "
                f"Subscription ID: {subscription.id}, User ID: {current_user.id}. "
                f"Attempting to cancel Stripe subscription.",
                exc_info=True
            )
            try:
                stripe.Subscription.modify(subscription.id, cancel_at_period_end=True)
                logger.warning(f"Cancelled Stripe subscription {subscription.id} due to database error")
            except Exception as cancel_error:
                logger.error(
                    f"Failed to cancel Stripe subscription {subscription.id}: {str(cancel_error)}. "
                    f"Manual cleanup required.",
                    exc_info=True
                )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save subscription. Please contact support."
            )
        
        logger.info(
            f"User {current_user.id} subscribed to {subscribe_request.plan} plan",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {
            "message": f"Successfully subscribed to {subscribe_request.plan} plan",
            "plan": subscribe_request.plan,
            "status": subscription.status,
            "customer_id": customer_id,
            "subscription_id": subscription.id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription. Please try again later."
        )


# --- Get Subscription Status Endpoint ---
@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current subscription status.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        
    Returns:
        Subscription status information
    """
    return {
        "plan": current_user.subscription_plan,
        "status": current_user.subscription_status,
        "customer_id": current_user.stripe_customer_id,
        "subscription_id": current_user.stripe_subscription_id
    }


# --- Cancel Subscription Endpoint ---
@router.post("/cancel", response_model=CancelResponse)
async def cancel_subscription(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel current subscription.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancellation confirmation
    """
    if not settings.BILLING_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing endpoints are currently disabled."
        )
    
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found."
        )
    
    try:
        # Cancel subscription in Stripe
        subscription = stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update user status
        current_user.subscription_status = "cancelled"
        await db.commit()
        
        logger.info(
            f"User {current_user.id} cancelled subscription",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {
            "message": "Subscription cancelled successfully. Access will continue until the end of the billing period.",
            "status": subscription.status
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during cancellation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription. Please try again later."
        )


# --- Stripe Webhook Endpoint ---
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    This endpoint processes webhook events from Stripe to keep user
    subscription status in sync.
    
    Args:
        request: FastAPI request object
        stripe_signature: Stripe signature header for webhook verification
        db: Database session
        
    Returns:
        Webhook processing result
    """
    if not settings.BILLING_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing endpoints are currently disabled."
        )
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret is not configured."
        )
    
    payload = await request.body()
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle different event types
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    try:
        if event_type == "customer.subscription.created":
            subscription_id = event_data["id"]
            customer_id = event_data["customer"]
            plan_metadata = event_data.get("metadata", {}).get("plan", "standard")
            
            # Find user by customer ID
            from sqlalchemy import select
            from app.models.user import User
            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                try:
                    user.stripe_subscription_id = subscription_id
                    user.subscription_plan = plan_metadata
                    user.subscription_status = event_data["status"]
                    await db.commit()
                    logger.info(f"Updated user {user.id} subscription from webhook: created")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from subscription.created webhook: {str(e)}", exc_info=True)
                    raise
        
        elif event_type == "customer.subscription.updated":
            subscription_id = event_data["id"]
            customer_id = event_data["customer"]
            
            # Find user by subscription ID or customer ID
            from sqlalchemy import select
            from app.models.user import User
            result = await db.execute(
                select(User).where(
                    (User.stripe_subscription_id == subscription_id) |
                    (User.stripe_customer_id == customer_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                try:
                    user.subscription_status = event_data["status"]
                    # Update plan if changed in metadata
                    if "metadata" in event_data and "plan" in event_data["metadata"]:
                        user.subscription_plan = event_data["metadata"]["plan"]
                    await db.commit()
                    logger.info(f"Updated user {user.id} subscription from webhook: updated")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from subscription.updated webhook: {str(e)}", exc_info=True)
                    raise
        
        elif event_type == "customer.subscription.deleted":
            subscription_id = event_data["id"]
            customer_id = event_data["customer"]
            
            # Find user by subscription ID or customer ID
            from sqlalchemy import select
            from app.models.user import User
            result = await db.execute(
                select(User).where(
                    (User.stripe_subscription_id == subscription_id) |
                    (User.stripe_customer_id == customer_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                try:
                    user.subscription_status = "cancelled"
                    user.subscription_plan = "standard"  # Downgrade to standard after cancellation
                    await db.commit()
                    logger.info(f"Updated user {user.id} subscription from webhook: deleted")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from subscription.deleted webhook: {str(e)}", exc_info=True)
                    raise
        
        elif event_type == "invoice.payment_failed":
            customer_id = event_data.get("customer")
            subscription_id = event_data.get("subscription")
            
            # Find user by customer ID or subscription ID
            from sqlalchemy import select
            from app.models.user import User
            result = await db.execute(
                select(User).where(
                    (User.stripe_customer_id == customer_id) |
                    (User.stripe_subscription_id == subscription_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                try:
                    # Update status to past_due (grace period)
                    user.subscription_status = "past_due"
                    await db.commit()
                    logger.info(f"Updated user {user.id} subscription status to past_due from payment_failed webhook")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from payment_failed webhook: {str(e)}", exc_info=True)
                    raise
        
        elif event_type == "invoice.payment_succeeded":
            customer_id = event_data.get("customer")
            subscription_id = event_data.get("subscription")
            
            # Find user by customer ID or subscription ID
            from sqlalchemy import select
            from app.models.user import User
            result = await db.execute(
                select(User).where(
                    (User.stripe_customer_id == customer_id) |
                    (User.stripe_subscription_id == subscription_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                try:
                    # Ensure status is active after successful payment
                    if user.subscription_status == "past_due":
                        user.subscription_status = "active"
                        await db.commit()
                        logger.info(f"Updated user {user.id} subscription status to active from payment_succeeded webhook")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from payment_succeeded webhook: {str(e)}", exc_info=True)
                    raise
        
        return JSONResponse(content={"status": "success"})
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )
