# --- Tracking Router ---
"""
Email tracking endpoints for open tracking pixels.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.db import get_db
from app.models.campaign_recipient import CampaignRecipient
from app.models.email_event import EmailEvent, EventType
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/track-open", tags=["tracking"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- 1x1 Transparent PNG (base64 encoded) ---
TRACKING_PIXEL = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'


@router.get("/{tracking_id}")
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
                metadata={
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

