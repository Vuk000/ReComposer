# --- Campaign Tasks ---
"""
Celery tasks for campaign operations.
"""

from celery import Task
from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def launch_campaign(campaign_id: int):
    """
    Launch a campaign by scheduling initial emails.
    
    This task is called when a campaign is launched.
    It creates CampaignRecipient entries and schedules initial emails.
    
    Args:
        campaign_id: Campaign ID to launch
    """
    # This is handled synchronously in the launch endpoint for now
    # Can be moved to async task if needed for large campaigns
    logger.info(f"Campaign {campaign_id} launch task (handled in endpoint)")
    return {"status": "handled_in_endpoint"}


@celery_app.task
def cancel_followups_for_contact(recipient_id: int):
    """
    Cancel scheduled follow-up emails for a contact that replied.
    
    Args:
        recipient_id: CampaignRecipient ID that received a reply
    """
    import asyncio
    from datetime import datetime, timezone
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.db import AsyncSessionLocal
    from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
    
    async def _cancel():
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(
                    select(CampaignRecipient).where(CampaignRecipient.id == recipient_id)
                )
                recipient = result.scalar_one_or_none()
                
                if recipient:
                    # Clear next_send_at to prevent further sends
                    recipient.next_send_at = None
                    await db.commit()
                    logger.info(f"Cancelled follow-ups for recipient {recipient_id}")
                    return {"success": True}
                else:
                    logger.warning(f"Recipient {recipient_id} not found")
                    return {"success": False, "error": "Recipient not found"}
                    
            except Exception as e:
                await db.rollback()
                logger.error(f"Error cancelling follow-ups: {str(e)}", exc_info=True)
                return {"success": False, "error": str(e)}
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_cancel())

