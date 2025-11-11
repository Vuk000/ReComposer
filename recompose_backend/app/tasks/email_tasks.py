# --- Email Tasks ---
"""
Celery tasks for email sending operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.celery_app import celery_app
from app.config import settings
from app.db import AsyncSessionLocal
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_email import CampaignEmail
from app.models.contact import Contact
from app.models.email_account import EmailAccount, EmailProvider
from app.services.email.email_sender import send_email, merge_template
from app.services.reply_detector import check_replies_for_user
import logging

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncSession:
    """Get database session for async operations."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@celery_app.task(bind=True, max_retries=3)
def send_campaign_email(self, recipient_id: int):
    """
    Send a single campaign email to a recipient.
    
    Args:
        recipient_id: CampaignRecipient ID
    """
    import asyncio
    
    async def _send():
        async with AsyncSessionLocal() as db:
            try:
                # Get recipient
                result = await db.execute(
                    select(CampaignRecipient).where(CampaignRecipient.id == recipient_id)
                )
                recipient = result.scalar_one_or_none()
                
                if not recipient:
                    logger.error(f"Recipient {recipient_id} not found")
                    return {"success": False, "error": "Recipient not found"}
                
                # Check if already sent or replied
                if recipient.status in [RecipientStatus.SENT, RecipientStatus.REPLIED]:
                    logger.info(f"Recipient {recipient_id} already {recipient.status.value}, skipping")
                    return {"success": True, "skipped": True}
                
                # Get campaign and check status
                campaign_result = await db.execute(
                    select(Campaign).where(Campaign.id == recipient.campaign_id)
                )
                campaign = campaign_result.scalar_one()
                
                if campaign.status != CampaignStatus.RUNNING:
                    logger.warning(f"Campaign {campaign.id} is not running, skipping send")
                    return {"success": False, "error": "Campaign not running"}
                
                # Get contact
                contact_result = await db.execute(
                    select(Contact).where(Contact.id == recipient.contact_id)
                )
                contact = contact_result.scalar_one()
                
                # Get email step
                next_step = recipient.current_step + 1
                email_result = await db.execute(
                    select(CampaignEmail).where(
                        CampaignEmail.campaign_id == campaign.id,
                        CampaignEmail.step_number == next_step
                    )
                )
                email_step = email_result.scalar_one_or_none()
                
                if not email_step:
                    # No more steps, mark as completed
                    recipient.status = RecipientStatus.SKIPPED
                    await db.commit()
                    return {"success": True, "completed": True}
                
                # Get user's default email account
                account_result = await db.execute(
                    select(EmailAccount).where(
                        EmailAccount.user_id == campaign.user_id,
                        EmailAccount.is_active == True,
                        EmailAccount.is_default == True
                    )
                )
                email_account = account_result.scalar_one_or_none()
                
                if not email_account:
                    recipient.status = RecipientStatus.FAILED
                    recipient.error_message = "No active email account configured"
                    await db.commit()
                    return {"success": False, "error": "No email account configured"}
                
                # Merge template
                subject = merge_template(email_step.subject, contact)
                body = merge_template(email_step.body_template, contact)
                
                # Generate HTML body for tracking (convert plain text to HTML if needed)
                html_body = None
                if recipient.tracking_id:
                    # Convert plain text to HTML with line breaks
                    html_body = body.replace('\n', '<br>\n')
                
                # Send email
                send_result = await send_email(
                    email_account=email_account,
                    to_email=contact.email,
                    to_name=contact.name,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                    campaign_id=campaign.id,
                    tracking_id=recipient.tracking_id
                )
                
                if send_result["success"]:
                    # Update recipient
                    recipient.status = RecipientStatus.SENT
                    recipient.current_step = next_step
                    recipient.last_sent_at = datetime.now(timezone.utc)
                    recipient.sent_message_id = send_result.get("message_id")
                    
                    # Schedule next step
                    delay = timedelta(days=email_step.delay_days, hours=email_step.delay_hours)
                    recipient.next_send_at = datetime.now(timezone.utc) + delay
                    
                    await db.commit()
                    logger.info(f"Sent email to recipient {recipient_id}, step {next_step}")
                    return {"success": True, "step": next_step}
                else:
                    # Mark as failed
                    recipient.status = RecipientStatus.FAILED
                    recipient.error_message = send_result.get("error", "Send failed")
                    await db.commit()
                    logger.error(f"Failed to send email to recipient {recipient_id}: {send_result.get('error')}")
                    return {"success": False, "error": send_result.get("error")}
                    
            except Exception as e:
                await db.rollback()
                logger.error(f"Error sending email to recipient {recipient_id}: {str(e)}", exc_info=True)
                raise
    
    # Run async function
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())


@celery_app.task
def process_pending_emails():
    """
    Process pending emails that are ready to be sent.
    Runs periodically (every minute).
    """
    import asyncio
    
    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.now(timezone.utc)
                
                # Find recipients ready to send
                result = await db.execute(
                    select(CampaignRecipient).where(
                        and_(
                            CampaignRecipient.status == RecipientStatus.PENDING,
                            CampaignRecipient.next_send_at <= now
                        )
                    ).limit(settings.MAX_EMAILS_PER_MINUTE)  # Rate limiting
                )
                recipients = result.scalars().all()
                
                if not recipients:
                    return {"processed": 0}
                
                # Send emails (rate limited)
                sent_count = 0
                for recipient in recipients:
                    try:
                        send_campaign_email.delay(recipient.id)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Error queuing email for recipient {recipient.id}: {str(e)}")
                
                logger.info(f"Queued {sent_count} emails for sending")
                return {"processed": sent_count}
                
            except Exception as e:
                logger.error(f"Error processing pending emails: {str(e)}", exc_info=True)
                return {"error": str(e)}
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process())


@celery_app.task
def check_replies():
    """
    Check for email replies across all active campaigns.
    Runs periodically (every 5-10 minutes).
    """
    import asyncio
    
    async def _check():
        async with AsyncSessionLocal() as db:
            try:
                # Get all users with running campaigns
                result = await db.execute(
                    select(Campaign.user_id).distinct().where(
                        Campaign.status == CampaignStatus.RUNNING
                    )
                )
                user_ids = [row[0] for row in result.all()]
                
                checked_count = 0
                for user_id in user_ids:
                    try:
                        await check_replies_for_user(user_id, db)
                        checked_count += 1
                    except Exception as e:
                        logger.error(f"Error checking replies for user {user_id}: {str(e)}")
                
                logger.info(f"Checked replies for {checked_count} users")
                return {"checked": checked_count}
                
            except Exception as e:
                logger.error(f"Error checking replies: {str(e)}", exc_info=True)
                return {"error": str(e)}
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_check())

