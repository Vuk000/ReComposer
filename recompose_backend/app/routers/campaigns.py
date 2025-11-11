# --- Campaigns Router ---
"""
Campaign management endpoints for creating and managing email campaigns.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from app.db import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_email import CampaignEmail
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.contact import Contact
from app.routers.auth import get_current_user
from app.config import settings
from app.tasks.email_tasks import send_campaign_email
import logging
import uuid

# --- Router Setup ---
router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class EmailStepCreate(BaseModel):
    """Email step creation model."""
    step_number: int = Field(..., ge=1, description="Step number in sequence (1 = initial)")
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body_template: str = Field(..., min_length=1, description="Email body template with placeholders")
    delay_days: int = Field(default=0, ge=0, description="Days to wait before sending this step")
    delay_hours: int = Field(default=0, ge=0, le=23, description="Additional hours for precise timing")


class CampaignCreate(BaseModel):
    """Campaign creation request model."""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, max_length=5000, description="Campaign description")
    contact_ids: List[int] = Field(..., min_length=1, description="List of contact IDs to include")
    email_steps: List[EmailStepCreate] = Field(..., min_length=1, description="Email steps in sequence")
    
    @field_validator("email_steps")
    @classmethod
    def validate_steps(cls, v: List[EmailStepCreate]) -> List[EmailStepCreate]:
        """Validate step numbers are sequential starting from 1."""
        step_numbers = [step.step_number for step in v]
        if len(step_numbers) != len(set(step_numbers)):
            raise ValueError("Step numbers must be unique")
        if min(step_numbers) != 1:
            raise ValueError("Step numbers must start from 1")
        if max(step_numbers) != len(step_numbers):
            raise ValueError("Step numbers must be sequential")
        return sorted(v, key=lambda x: x.step_number)


class CampaignUpdate(BaseModel):
    """Campaign update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)


class CampaignEmailResponse(BaseModel):
    """Campaign email response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    step_number: int
    subject: str
    body_template: str
    delay_days: int
    delay_hours: int
    created_at: datetime


class CampaignResponse(BaseModel):
    """Campaign response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    status: CampaignStatus
    created_at: datetime
    launched_at: Optional[datetime]
    paused_at: Optional[datetime]
    email_steps: List[CampaignEmailResponse]
    stats: Optional[dict] = None


class CampaignListResponse(BaseModel):
    """Paginated campaigns list response."""
    campaigns: List[CampaignResponse]
    total: int
    limit: int
    offset: int


class CampaignRecipientResponse(BaseModel):
    """Campaign recipient response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contact_id: int
    contact_name: str
    contact_email: str
    current_step: int
    status: RecipientStatus
    last_sent_at: Optional[datetime]
    next_send_at: Optional[datetime]
    open_count: int
    reply_detected_at: Optional[datetime]
    error_message: Optional[str]


class CampaignRecipientsListResponse(BaseModel):
    """Paginated campaign recipients list response."""
    recipients: List[CampaignRecipientResponse]
    total: int
    limit: int
    offset: int


# --- Helper Functions ---
async def check_campaign_ownership(campaign_id: int, user_id: int, db: AsyncSession) -> Campaign:
    """Check if campaign exists and belongs to user."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


async def get_campaign_stats(campaign_id: int, db: AsyncSession) -> dict:
    """Get aggregate statistics for a campaign."""
    # Count recipients by status
    status_counts = await db.execute(
        select(
            CampaignRecipient.status,
            func.count(CampaignRecipient.id).label('count')
        )
        .where(CampaignRecipient.campaign_id == campaign_id)
        .group_by(CampaignRecipient.status)
    )
    
    stats = {
        "total_recipients": 0,
        "pending": 0,
        "sent": 0,
        "replied": 0,
        "bounced": 0,
        "failed": 0,
        "skipped": 0,
        "total_opens": 0,
    }
    
    for row in status_counts:
        status_name = row.status.value.lower()
        count = row.count
        stats[status_name] = count
        stats["total_recipients"] += count
    
    # Get total opens
    opens_result = await db.execute(
        select(func.sum(CampaignRecipient.open_count))
        .where(CampaignRecipient.campaign_id == campaign_id)
    )
    stats["total_opens"] = opens_result.scalar() or 0
    
    return stats


# --- Endpoints ---
@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: Request,
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign in Draft status."""
    # Verify all contacts belong to user
    contacts_result = await db.execute(
        select(Contact).where(
            Contact.id.in_(campaign_data.contact_ids),
            Contact.user_id == current_user.id
        )
    )
    found_contacts = contacts_result.scalars().all()
    
    if len(found_contacts) != len(campaign_data.contact_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more contacts not found or do not belong to user"
        )
    
    # Create campaign in transaction
    try:
        campaign = Campaign(
            user_id=current_user.id,
            name=campaign_data.name,
            description=campaign_data.description,
            status=CampaignStatus.DRAFT
        )
        db.add(campaign)
        await db.flush()  # Get campaign ID
        
        # Create email steps
        for step_data in campaign_data.email_steps:
            campaign_email = CampaignEmail(
                campaign_id=campaign.id,
                step_number=step_data.step_number,
                subject=step_data.subject,
                body_template=step_data.body_template,
                delay_days=step_data.delay_days,
                delay_hours=step_data.delay_hours
            )
            db.add(campaign_email)
        
        # Create campaign recipients
        for contact in found_contacts:
            recipient = CampaignRecipient(
                campaign_id=campaign.id,
                contact_id=contact.id,
                status=RecipientStatus.PENDING,
                current_step=0
            )
            recipient.generate_tracking_id()
            db.add(recipient)
        
        await db.commit()
        await db.refresh(campaign)
        
        # Load relationships
        await db.refresh(campaign, ["campaign_emails"])
        
        logger.info(
            f"User {current_user.id} created campaign {campaign.id} with {len(found_contacts)} recipients",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return campaign
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating campaign: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign"
        )


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: Optional[CampaignStatus] = Query(None, alias="status")
):
    """List campaigns with pagination and status filter."""
    query = select(Campaign).where(Campaign.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(Campaign.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    # Load email steps for each campaign
    campaign_responses = []
    for campaign in campaigns:
        await db.refresh(campaign, ["campaign_emails"])
        campaign_dict = {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "status": campaign.status,
            "created_at": campaign.created_at,
            "launched_at": campaign.launched_at,
            "paused_at": campaign.paused_at,
            "email_steps": [
                CampaignEmailResponse(
                    id=email.id,
                    step_number=email.step_number,
                    subject=email.subject,
                    body_template=email.body_template,
                    delay_days=email.delay_days,
                    delay_hours=email.delay_hours,
                    created_at=email.created_at
                )
                for email in campaign.campaign_emails
            ],
            "stats": None
        }
        campaign_responses.append(campaign_dict)
    
    return {
        "campaigns": campaign_responses,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    request: Request,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign with statistics."""
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    # Load relationships
    await db.refresh(campaign, ["campaign_emails"])
    
    # Get stats
    stats = await get_campaign_stats(campaign_id, db)
    
    campaign_dict = {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "status": campaign.status,
        "created_at": campaign.created_at,
        "launched_at": campaign.launched_at,
        "paused_at": campaign.paused_at,
        "email_steps": [
            CampaignEmailResponse(
                id=email.id,
                step_number=email.step_number,
                subject=email.subject,
                body_template=email.body_template,
                delay_days=email.delay_days,
                delay_hours=email.delay_hours,
                created_at=email.created_at
            )
            for email in campaign.campaign_emails
        ],
        "stats": stats
    }
    
    return campaign_dict


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    request: Request,
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign (only if Draft status)."""
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update campaigns in Draft status"
        )
    
    if campaign_data.name is not None:
        campaign.name = campaign_data.name
    if campaign_data.description is not None:
        campaign.description = campaign_data.description
    
    await db.commit()
    await db.refresh(campaign)
    await db.refresh(campaign, ["campaign_emails"])
    
    logger.info(
        f"User {current_user.id} updated campaign {campaign_id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    request: Request,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign (only if Draft or Cancelled)."""
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete campaigns in Draft or Cancelled status"
        )
    
    await db.delete(campaign)
    await db.commit()
    
    logger.info(
        f"User {current_user.id} deleted campaign {campaign_id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return None


@router.post("/{campaign_id}/launch", response_model=dict)
async def launch_campaign(
    request: Request,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Launch a campaign (Pro plan only)."""
    # Check Pro plan
    if current_user.subscription_plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign launching requires Pro plan"
        )
    
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only launch campaigns in Draft status"
        )
    
    # Check if campaign has email steps
    await db.refresh(campaign, ["campaign_emails"])
    if not campaign.campaign_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign must have at least one email step"
        )
    
    # Update campaign status
    campaign.status = CampaignStatus.RUNNING
    campaign.launched_at = datetime.now(timezone.utc)
    
    # Get first email step
    first_step = min(campaign.campaign_emails, key=lambda x: x.step_number)
    
    # Schedule initial emails for all recipients
    now = datetime.now(timezone.utc)
    recipients_result = await db.execute(
        select(CampaignRecipient).where(CampaignRecipient.campaign_id == campaign_id)
    )
    recipients = recipients_result.scalars().all()
    
    for recipient in recipients:
        recipient.status = RecipientStatus.PENDING
        recipient.next_send_at = now  # Send immediately for first step
        recipient.generate_tracking_id()
    
    await db.commit()
    
    # Trigger Celery tasks to send initial emails immediately
    for recipient in recipients:
        try:
            send_campaign_email.delay(recipient.id)
        except Exception as e:
            logger.error(f"Error queuing email task for recipient {recipient.id}: {str(e)}")
    
    logger.info(
        f"User {current_user.id} launched campaign {campaign_id} with {len(recipients)} recipients",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {
        "message": "Campaign launched successfully",
        "campaign_id": campaign_id,
        "recipients_scheduled": len(recipients)
    }


@router.post("/{campaign_id}/pause", response_model=dict)
async def pause_campaign(
    request: Request,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a running campaign."""
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    if campaign.status != CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pause running campaigns"
        )
    
    campaign.status = CampaignStatus.PAUSED
    campaign.paused_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    logger.info(
        f"User {current_user.id} paused campaign {campaign_id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {"message": "Campaign paused successfully"}


@router.get("/{campaign_id}/recipients", response_model=CampaignRecipientsListResponse)
async def get_campaign_recipients(
    request: Request,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: Optional[RecipientStatus] = Query(None, alias="status")
):
    """Get campaign recipients with pagination."""
    # Verify campaign ownership
    campaign = await check_campaign_ownership(campaign_id, current_user.id, db)
    
    # Build query
    query = select(CampaignRecipient, Contact).join(
        Contact, CampaignRecipient.contact_id == Contact.id
    ).where(CampaignRecipient.campaign_id == campaign_id)
    
    if status_filter:
        query = query.where(CampaignRecipient.status == status_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(CampaignRecipient.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.all()
    
    recipients = []
    for recipient, contact in rows:
        recipients.append({
            "id": recipient.id,
            "contact_id": contact.id,
            "contact_name": contact.name,
            "contact_email": contact.email,
            "current_step": recipient.current_step,
            "status": recipient.status,
            "last_sent_at": recipient.last_sent_at,
            "next_send_at": recipient.next_send_at,
            "open_count": recipient.open_count,
            "reply_detected_at": recipient.reply_detected_at,
            "error_message": recipient.error_message
        })
    
    return {
        "recipients": recipients,
        "total": total,
        "limit": limit,
        "offset": offset
    }

