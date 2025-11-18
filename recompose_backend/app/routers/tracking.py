# --- Tracking Router ---
"""
Email tracking endpoints for open tracking pixels.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional
from app.db import get_db
from app.models.campaign_recipient import CampaignRecipient
from app.models.email_event import EmailEvent, EventType
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api", tags=["tracking"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- 1x1 Transparent PNG (base64 encoded) ---
TRACKING_PIXEL = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'


@router.get("/track-open/{tracking_id}")
async def track_open(
    request: Request,
    tracking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Track email open event via tracking pixel.
    
    Returns a 1x1 transparent PNG image and logs the open event.
    
    Args:
        request: FastAPI request object
        tracking_id: Unique tracking ID from email
        db: Database session
        
    Returns:
        1x1 transparent PNG image
    """
    try:
        # Find recipient by tracking ID
        result = await db.execute(
            select(CampaignRecipient).where(CampaignRecipient.tracking_id == tracking_id)
        )
        recipient = result.scalar_one_or_none()
        
        if not recipient:
            # Still return pixel even if tracking ID not found (to prevent enumeration)
            logger.warning(f"Tracking ID not found: {tracking_id}")
            return Response(content=TRACKING_PIXEL, media_type="image/png")
        
        # Check if already opened (to avoid duplicate events)
        # We'll still increment open_count but only log event once per day
        now = datetime.now(timezone.utc)
        
        # Increment open count
        recipient.open_count += 1
        
        # Log open event (only if not opened today)
        # Check if there's already an OPEN event today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        existing_event = await db.execute(
            select(EmailEvent).where(
                EmailEvent.campaign_recipient_id == recipient.id,
                EmailEvent.event_type == EventType.OPEN,
                EmailEvent.timestamp >= today_start
            )
        )
        
        if not existing_event.scalar_one_or_none():
            # Create new open event
            event = EmailEvent(
                campaign_recipient_id=recipient.id,
                event_type=EventType.OPEN,
                timestamp=now,
                event_metadata={
                    "ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent", "")
                }
            )
            db.add(event)
        
        await db.commit()
        
        logger.info(
            f"Email opened: tracking_id={tracking_id}, recipient_id={recipient.id}, open_count={recipient.open_count}",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        # Return 1x1 transparent PNG
        return Response(content=TRACKING_PIXEL, media_type="image/png")
        
    except Exception as e:
        logger.error(f"Error tracking email open: {str(e)}", exc_info=True)
        # Still return pixel even on error
        return Response(content=TRACKING_PIXEL, media_type="image/png")


@router.get("/click/{tracking_id}")
async def track_click(
    request: Request,
    tracking_id: str,
    url: str = Query(..., description="Target URL to redirect to"),
    db: AsyncSession = Depends(get_db)
):
    """
    Track email click event and redirect to target URL.
    
    Args:
        request: FastAPI request object
        tracking_id: Unique tracking ID from email link
        url: Target URL to redirect to (URL encoded)
        db: Database session
        
    Returns:
        Redirect response to target URL
    """
    try:
        # Find recipient by tracking ID
        result = await db.execute(
            select(CampaignRecipient).where(CampaignRecipient.tracking_id == tracking_id)
        )
        recipient = result.scalar_one_or_none()
        
        if not recipient:
            # Still redirect even if tracking ID not found
            logger.warning(f"Tracking ID not found for click: {tracking_id}")
            return RedirectResponse(url=url, status_code=302)
        
        # Log click event
        now = datetime.now(timezone.utc)
        event = EmailEvent(
            campaign_recipient_id=recipient.id,
            event_type=EventType.CLICK,
            timestamp=now,
            event_metadata={
                "type": "click",
                "url": url,
                "ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", "")
            }
        )
        db.add(event)
        await db.commit()
        
        logger.info(
            f"Email clicked: tracking_id={tracking_id}, recipient_id={recipient.id}, url={url}",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        # Redirect to target URL
        return RedirectResponse(url=url, status_code=302)
        
    except Exception as e:
        logger.error(f"Error tracking email click: {str(e)}", exc_info=True)
        # Still redirect even on error
        try:
            return RedirectResponse(url=url, status_code=302)
        except:
            return Response(content="Redirect failed", status_code=500)


@router.get("/pixel/{tracking_id}.png")
async def track_open_pixel(
    request: Request,
    tracking_id: str,
    email_id: Optional[str] = Query(None, description="Email ID for additional tracking"),
    db: AsyncSession = Depends(get_db)
):
    """
    Track email open event via tracking pixel (alternative endpoint format).
    
    Returns a 1x1 transparent PNG image and logs the open event.
    This endpoint matches the format: /pixel/{user_id}.png?email_id=xxx
    
    Args:
        request: FastAPI request object
        tracking_id: Unique tracking ID (can be user_id or recipient tracking_id)
        email_id: Optional email ID for additional tracking
        db: Database session
        
    Returns:
        1x1 transparent PNG image
    """
    # Try to find by tracking_id first (campaign recipient)
    result = await db.execute(
        select(CampaignRecipient).where(CampaignRecipient.tracking_id == tracking_id)
    )
    recipient = result.scalar_one_or_none()
    
    if recipient:
        # Use the existing track_open logic
        return await track_open(request, tracking_id, db)
    
    # If not found, still return pixel (prevents enumeration)
    logger.debug(f"Tracking ID not found for pixel: {tracking_id}, email_id={email_id}")
    return Response(content=TRACKING_PIXEL, media_type="image/png")

