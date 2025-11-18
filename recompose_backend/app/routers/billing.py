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
router = APIRouter(prefix="/api/billing", tags=["billing"])

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


class CreateCheckoutRequest(BaseModel):
    """Create checkout session request model."""
    plan: str  # "standard" or "pro"
    interval: str = "month"  # "month" or "year"
    success_url: Optional[str] = None  # URL to redirect after success
    cancel_url: Optional[str] = None  # URL to redirect after cancel


class CreateCheckoutResponse(BaseModel):
    """Create checkout session response model."""
    checkout_url: str
    session_id: str


class CreatePortalResponse(BaseModel):
    """Create customer portal session response model."""
    portal_url: str


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


def get_stripe_lookup_key(plan: str, interval: str = "month") -> str:
    """
    Get Stripe lookup key for plan and interval.
    
    Args:
        plan: Plan name (standard, pro)
        interval: Billing interval (month, year)
        
    Returns:
        Stripe lookup key
        
    Raises:
        ValueError: If lookup key is not configured for the plan/interval
    """
    try:
        if interval == "year":
            lookup_map = {
                "standard": getattr(settings, 'STRIPE_STANDARD_YEARLY_LOOKUP_KEY', None),
                "pro": getattr(settings, 'STRIPE_PRO_YEARLY_LOOKUP_KEY', None),
            }
        else:
            lookup_map = {
                "standard": getattr(settings, 'STRIPE_STANDARD_MONTHLY_LOOKUP_KEY', None),
                "pro": getattr(settings, 'STRIPE_PRO_MONTHLY_LOOKUP_KEY', None),
            }
        
        lookup_key = lookup_map.get(plan)
        if not lookup_key:
            raise ValueError(f"Lookup key not configured for plan: {plan}, interval: {interval}. Please set STRIPE_{plan.upper()}_{interval.upper()}_LOOKUP_KEY in environment variables.")
        
        return lookup_key
    except AttributeError as e:
        raise ValueError(f"Lookup key configuration error: {str(e)}")


# --- Create Checkout Session Endpoint ---
@router.post("/create-checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: Request,
    checkout_request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        request: FastAPI request object
        checkout_request: Checkout session request with plan and interval
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Checkout session URL
    """
    if not settings.BILLING_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing endpoints are currently disabled."
        )
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is not configured."
        )
    
    valid_plans = ["standard", "pro"]
    valid_intervals = ["month", "year"]
    
    if checkout_request.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan must be one of: {', '.join(valid_plans)}"
        )
    
    if checkout_request.interval not in valid_intervals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interval must be one of: {', '.join(valid_intervals)}"
        )
    
    try:
        # Get or create Stripe customer
        customer_id = await get_or_create_stripe_customer(current_user)
        
        # Get lookup key
        try:
            lookup_key = get_stripe_lookup_key(checkout_request.plan, checkout_request.interval)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lookup key not configured for plan {checkout_request.plan} ({checkout_request.interval})"
            )
        
        # Set success and cancel URLs
        success_url = checkout_request.success_url or f"{settings.FRONTEND_URL}/app/dashboard?checkout=success"
        cancel_url = checkout_request.cancel_url or f"{settings.FRONTEND_URL}/?checkout=cancelled"
        
        # Create checkout session using lookup key
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_lookup_key": lookup_key,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "plan": checkout_request.plan,
                "interval": checkout_request.interval
            },
            allow_promotion_codes=True,
        )
        
        logger.info(
            f"Created checkout session for user {current_user.id}, plan={checkout_request.plan}, interval={checkout_request.interval}",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session."
        )


# --- Create Customer Portal Session Endpoint ---
@router.post("/customer-portal", response_model=CreatePortalResponse)
async def create_customer_portal_session(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe customer portal session for managing subscription.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Customer portal session URL
    """
    if not settings.BILLING_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing endpoints are currently disabled."
        )
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is not configured."
        )
    
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found. Please subscribe first."
        )
    
    try:
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/settings",
        )
        
        logger.info(
            f"Created customer portal session for user {current_user.id}",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {
            "portal_url": portal_session.url
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portal session."
        )


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
        
        # Get lookup key for plan (default to monthly)
        try:
            lookup_key = get_stripe_lookup_key(subscribe_request.plan, "month")
        except ValueError:
            # Fallback: if lookup keys aren't configured, create subscription with price_data
            logger.warning(f"Lookup key not configured for plan {subscribe_request.plan}, using price_data")
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
            # Create subscription with lookup key
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price_lookup_key": lookup_key}],
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
    # Return only plan and status to match frontend expectations
    # Frontend can get full details from user profile if needed
    return {
        "plan": current_user.subscription_plan or "standard",
        "status": current_user.subscription_status or "active",
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
        if event_type == "checkout.session.completed":
            # Handle successful checkout completion
            session = event_data
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")
            metadata = session.get("metadata", {})
            plan = metadata.get("plan", "standard")
            
            # Find user by customer ID or metadata
            from sqlalchemy import select
            from app.models.user import User
            user = None
            if customer_id:
                result = await db.execute(
                    select(User).where(User.stripe_customer_id == customer_id)
                )
                user = result.scalar_one_or_none()
            elif "user_id" in metadata:
                result = await db.execute(
                    select(User).where(User.id == int(metadata["user_id"]))
                )
                user = result.scalar_one_or_none()
            
            if user:
                try:
                    user.stripe_customer_id = customer_id or user.stripe_customer_id
                    if subscription_id:
                        user.stripe_subscription_id = subscription_id
                    user.subscription_plan = plan
                    user.subscription_status = "active"
                    await db.commit()
                    logger.info(f"Updated user {user.id} from checkout.session.completed webhook, plan={plan}")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user {user.id} from checkout.session.completed webhook: {str(e)}", exc_info=True)
                    raise
        
        elif event_type == "customer.subscription.created":
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
