# --- Brevo Webhook Router ---
"""
Brevo webhook endpoints for email event tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel
import hmac
import hashlib
import json
import logging
from app.db import get_db
from app.config import settings
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.email_event import EmailEvent, EventType

# --- Router Setup ---
router = APIRouter(prefix="/api/brevo", tags=["brevo-webhook"])

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class BrevoWebhookEvent(BaseModel):
    """Brevo webhook event model."""
    event: str
    email: str
    id: Optional[int] = None
    date: Optional[str] = None
    ts: Optional[int] = None
    message_id: Optional[str] = None
    tags: Optional[list] = None
    sending_ip: Optional[str] = None
    ts_event: Optional[int] = None
    subject: Optional[str] = None
    ts_epoch: Optional[int] = None
    link: Optional[str] = None
    reason: Optional[str] = None
    tag: Optional[str] = None


def verify_brevo_signature(payload: bytes, signature: Optional[str]) -> bool:
    """
    Verify Brevo webhook signature.
    
    Args:
        payload: Raw request body
        signature: Signature from X-Brevo-Signature header
        
    Returns:
        True if signature is valid
    """
    if not settings.BREVO_WEBHOOK_SECRET or not signature:
        # If no secret configured, skip verification (not recommended for production)
        logger.warning("Brevo webhook secret not configured, skipping signature verification")
        return True
    
    try:
        # Brevo uses HMAC SHA256
        expected_signature = hmac.new(
            settings.BREVO_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying Brevo signature: {str(e)}")
        return False


@router.post("/webhook")
async def brevo_webhook(
    request: Request,
    event: BrevoWebhookEvent,
    x_brevo_signature: Optional[str] = Header(None, alias="X-Brevo-Signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Brevo webhook events.
    
    Supported events:
    - request: Email requested to be sent
    - delivered: Email delivered
    - hard_bounce: Hard bounce
    - soft_bounce: Soft bounce
    - blocked: Email blocked
    - spam: Marked as spam
    - invalid_email: Invalid email address
    - deferred: Email deferred
    - opened: Email opened
    - clicked: Link clicked
    - unsubscribed: Unsubscribed
    - complaint: Complaint (spam report)
    
    Args:
        request: FastAPI request object
        event: Brevo webhook event
        x_brevo_signature: Webhook signature for verification
        db: Database session
        
    Returns:
        Success response
    """
    try:
        # Verify signature
        body = await request.body()
        if not verify_brevo_signature(body, x_brevo_signature):
            logger.warning(f"Invalid Brevo webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Find recipient by email and message_id
        recipient = None
        if event.message_id:
            # Try to find by message_id (stored in sent_message_id)
            result = await db.execute(
                select(CampaignRecipient).where(
                    CampaignRecipient.sent_message_id == str(event.message_id)
                )
            )
            recipient = result.scalar_one_or_none()
        
        if not recipient and event.email:
            # Try to find by email (less reliable, but fallback)
            from app.models.contact import Contact
            contact_result = await db.execute(
                select(Contact).where(Contact.email == event.email)
            )
            contact = contact_result.scalar_one_or_none()
            if contact:
                # Get most recent recipient for this contact
                recipient_result = await db.execute(
                    select(CampaignRecipient)
                    .where(CampaignRecipient.contact_id == contact.id)
                    .order_by(CampaignRecipient.last_sent_at.desc())
                    .limit(1)
                )
                recipient = recipient_result.scalar_one_or_none()
        
        if not recipient:
            logger.debug(f"Recipient not found for Brevo event: {event.event}, email={event.email}, message_id={event.message_id}")
            # Still return success to Brevo
            return JSONResponse(content={"status": "ok", "message": "Event processed"})
        
        # Process event based on type
        now = datetime.now(timezone.utc)
        event_metadata = {
            "brevo_event": event.event,
            "brevo_message_id": event.message_id,
            "brevo_date": event.date,
            "brevo_ts": event.ts,
        }
        
        if event.event == "delivered":
            # Email delivered successfully
            if recipient.status == RecipientStatus.PENDING:
                recipient.status = RecipientStatus.SENT
            recipient.last_sent_at = now
            
        elif event.event in ["hard_bounce", "soft_bounce"]:
            # Email bounced
            recipient.status = RecipientStatus.BOUNCED
            recipient.error_message = f"Bounce: {event.reason or event.event}"
            event_metadata["reason"] = event.reason
            
        elif event.event == "blocked":
            # Email blocked
            recipient.status = RecipientStatus.FAILED
            recipient.error_message = f"Blocked: {event.reason or 'Email blocked'}"
            event_metadata["reason"] = event.reason
            
        elif event.event == "spam":
            # Marked as spam
            event_metadata["spam"] = True
            
        elif event.event == "invalid_email":
            # Invalid email address
            recipient.status = RecipientStatus.FAILED
            recipient.error_message = "Invalid email address"
            
        elif event.event == "opened":
            # Email opened (tracked via pixel, but also log webhook event)
            recipient.open_count += 1
            event_obj = EmailEvent(
                campaign_recipient_id=recipient.id,
                event_type=EventType.OPEN,
                timestamp=now,
                event_metadata=event_metadata
            )
            db.add(event_obj)
            
        elif event.event == "clicked":
            # Link clicked
            event_metadata["link"] = event.link
            event_obj = EmailEvent(
                campaign_recipient_id=recipient.id,
                event_type=EventType.CLICK,
                timestamp=now,
                event_metadata=event_metadata
            )
            db.add(event_obj)
            
        elif event.event == "unsubscribed":
            # Unsubscribed
            recipient.status = RecipientStatus.SKIPPED
            recipient.error_message = "Unsubscribed"
            
        elif event.event == "complaint":
            # Spam complaint
            event_metadata["complaint"] = True
            recipient.status = RecipientStatus.SKIPPED
            recipient.error_message = "Spam complaint"
        
        await db.commit()
        
        logger.info(
            f"Processed Brevo webhook event: {event.event} for recipient {recipient.id}",
            extra={"brevo_event": event.event, "recipient_id": recipient.id}
        )
        
        return JSONResponse(content={"status": "ok", "message": "Event processed"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Brevo webhook: {str(e)}", exc_info=True)
        # Still return success to Brevo to prevent retries
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=200)

