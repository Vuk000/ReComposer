# --- Reply Detector Service ---
"""
Service for detecting email replies via Gmail/Outlook APIs.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import User
from app.models.email_account import EmailAccount, EmailProvider
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.email_event import EmailEvent, EventType
from app.models.campaign import Campaign, CampaignStatus
from app.services.email.gmail_service import check_replies_gmail
from app.services.email.outlook_service import check_replies_outlook
from app.tasks.campaign_tasks import cancel_followups_for_contact
import logging

logger = logging.getLogger(__name__)


async def check_replies_for_user(user_id: int, db: AsyncSession) -> dict:
    """
    Check for replies for all active campaigns of a user.
    
    Args:
        user_id: User ID to check replies for
        db: Database session
        
    Returns:
        Dictionary with check results
    """
    try:
        # Get user's active email accounts
        accounts_result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.user_id == user_id,
                EmailAccount.is_active == True
            )
        )
        accounts = accounts_result.scalars().all()
        
        if not accounts:
            return {"checked": 0, "replies_found": 0}
        
        # Get user's running campaigns
        campaigns_result = await db.execute(
            select(Campaign).where(
                Campaign.user_id == user_id,
                Campaign.status == CampaignStatus.RUNNING
            )
        )
        campaigns = campaigns_result.scalars().all()
        
        if not campaigns:
            return {"checked": 0, "replies_found": 0}
        
        # Get recipients that have been sent emails (not replied yet)
        campaign_ids = [c.id for c in campaigns]
        recipients_result = await db.execute(
            select(CampaignRecipient).where(
                CampaignRecipient.campaign_id.in_(campaign_ids),
                CampaignRecipient.status == RecipientStatus.SENT
            )
        )
        recipients = recipients_result.scalars().all()
        
        if not recipients:
            return {"checked": 0, "replies_found": 0}
        
        # Check replies for each account
        replies_found = 0
        for account in accounts:
            try:
                if account.provider == EmailProvider.GMAIL:
                    reply_message_ids = await check_replies_gmail(account)
                elif account.provider == EmailProvider.OUTLOOK:
                    reply_message_ids = await check_replies_outlook(account)
                else:
                    # SMTP doesn't support reply detection
                    continue
                
                # Match replies to recipients by message ID or thread
                # For now, we'll use a simple approach: check if any sent message IDs match
                # In full implementation, we'd use thread IDs or headers
                for recipient in recipients:
                    if recipient.sent_message_id and recipient.sent_message_id in reply_message_ids:
                        # Reply detected!
                        await mark_recipient_as_replied(recipient.id, db)
                        replies_found += 1
                        
            except Exception as e:
                logger.error(f"Error checking replies for account {account.id}: {str(e)}")
        
        await db.commit()
        return {"checked": len(accounts), "replies_found": replies_found}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error checking replies for user {user_id}: {str(e)}", exc_info=True)
        raise


async def mark_recipient_as_replied(recipient_id: int, db: AsyncSession) -> None:
    """
    Mark a recipient as replied and cancel follow-ups.
    
    Args:
        recipient_id: CampaignRecipient ID
        db: Database session
    """
    result = await db.execute(
        select(CampaignRecipient).where(CampaignRecipient.id == recipient_id)
    )
    recipient = result.scalar_one_or_none()
    
    if not recipient or recipient.status == RecipientStatus.REPLIED:
        return
    
    # Update status
    recipient.status = RecipientStatus.REPLIED
    recipient.reply_detected_at = datetime.now(timezone.utc)
    recipient.next_send_at = None  # Cancel future sends
    
    # Create reply event
    event = EmailEvent(
        campaign_recipient_id=recipient.id,
        event_type=EventType.REPLY,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(event)
    
    # Trigger task to cancel follow-ups (async)
    cancel_followups_for_contact.delay(recipient_id)
    
    logger.info(f"Marked recipient {recipient_id} as replied")

