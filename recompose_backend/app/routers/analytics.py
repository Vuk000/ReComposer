# --- Analytics Router ---
"""
Analytics endpoints for dashboard statistics.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.email_event import EmailEvent, EventType
from app.models.contact import Contact
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class UsageStats(BaseModel):
    """Usage statistics model."""
    total_rewrites: int
    rewrites_today: int
    rewrites_this_week: int
    rewrites_this_month: int
    daily_limit: int
    remaining_today: int
    plan: str


class CampaignStats(BaseModel):
    """Campaign statistics model."""
    total_campaigns: int
    active_campaigns: int
    total_recipients: int
    sent_emails: int
    open_rate: float
    click_rate: float
    reply_rate: float


class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    usage: UsageStats
    campaigns: CampaignStats
    recent_activity: list[dict]


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analytics for the dashboard.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analytics data including usage, campaigns, and recent activity
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    # --- Usage Statistics ---
    # Total rewrites
    total_rewrites_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(RewriteLog.user_id == current_user.id)
    )
    total_rewrites = total_rewrites_result.scalar() or 0
    
    # Rewrites today
    rewrites_today_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(
            RewriteLog.user_id == current_user.id,
            RewriteLog.created_at >= today_start
        )
    )
    rewrites_today = rewrites_today_result.scalar() or 0
    
    # Rewrites this week
    rewrites_week_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(
            RewriteLog.user_id == current_user.id,
            RewriteLog.created_at >= week_start
        )
    )
    rewrites_this_week = rewrites_week_result.scalar() or 0
    
    # Rewrites this month
    rewrites_month_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(
            RewriteLog.user_id == current_user.id,
            RewriteLog.created_at >= month_start
        )
    )
    rewrites_this_month = rewrites_month_result.scalar() or 0
    
    # Daily limit based on plan
    if current_user.subscription_plan == "pro":
        daily_limit = 1000  # Effectively unlimited
    else:
        daily_limit = 20  # Standard plan limit
    
    remaining_today = max(0, daily_limit - rewrites_today)
    
    # --- Campaign Statistics ---
    # Total campaigns
    total_campaigns_result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.user_id == current_user.id)
    )
    total_campaigns = total_campaigns_result.scalar() or 0
    
    # Active campaigns
    active_campaigns_result = await db.execute(
        select(func.count(Campaign.id))
        .where(
            Campaign.user_id == current_user.id,
            Campaign.status == CampaignStatus.RUNNING
        )
    )
    active_campaigns = active_campaigns_result.scalar() or 0
    
    # Total recipients across all campaigns
    total_recipients_result = await db.execute(
        select(func.count(CampaignRecipient.id))
        .join(Campaign, CampaignRecipient.campaign_id == Campaign.id)
        .where(Campaign.user_id == current_user.id)
    )
    total_recipients = total_recipients_result.scalar() or 0
    
    # Sent emails
    sent_emails_result = await db.execute(
        select(func.count(CampaignRecipient.id))
        .join(Campaign, CampaignRecipient.campaign_id == Campaign.id)
        .where(
            Campaign.user_id == current_user.id,
            CampaignRecipient.status == RecipientStatus.SENT
        )
    )
    sent_emails = sent_emails_result.scalar() or 0
    
    # Open rate (opens / sent)
    total_opens_result = await db.execute(
        select(func.sum(CampaignRecipient.open_count))
        .join(Campaign, CampaignRecipient.campaign_id == Campaign.id)
        .where(
            Campaign.user_id == current_user.id,
            CampaignRecipient.status == RecipientStatus.SENT
        )
    )
    total_opens = total_opens_result.scalar() or 0
    
    open_rate = (total_opens / sent_emails * 100) if sent_emails > 0 else 0.0
    
    # Click rate (clicks / sent)
    click_events_result = await db.execute(
        select(func.count(EmailEvent.id))
        .join(CampaignRecipient, EmailEvent.campaign_recipient_id == CampaignRecipient.id)
        .join(Campaign, CampaignRecipient.campaign_id == Campaign.id)
        .where(
            Campaign.user_id == current_user.id,
            EmailEvent.event_type == EventType.CLICK
        )
    )
    total_clicks = click_events_result.scalar() or 0
    
    click_rate = (total_clicks / sent_emails * 100) if sent_emails > 0 else 0.0
    
    # Reply rate (replies / sent)
    replied_recipients_result = await db.execute(
        select(func.count(CampaignRecipient.id))
        .join(Campaign, CampaignRecipient.campaign_id == Campaign.id)
        .where(
            Campaign.user_id == current_user.id,
            CampaignRecipient.status == RecipientStatus.REPLIED
        )
    )
    replied_recipients = replied_recipients_result.scalar() or 0
    
    reply_rate = (replied_recipients / sent_emails * 100) if sent_emails > 0 else 0.0
    
    # --- Recent Activity ---
    # Get recent rewrite logs
    recent_rewrites_result = await db.execute(
        select(RewriteLog)
        .where(RewriteLog.user_id == current_user.id)
        .order_by(RewriteLog.created_at.desc())
        .limit(5)
    )
    recent_rewrites = recent_rewrites_result.scalars().all()
    
    # Get recent campaigns
    recent_campaigns_result = await db.execute(
        select(Campaign)
        .where(Campaign.user_id == current_user.id)
        .order_by(Campaign.created_at.desc())
        .limit(5)
    )
    recent_campaigns = recent_campaigns_result.scalars().all()
    
    # Format recent activity
    recent_activity = []
    for rewrite in recent_rewrites:
        recent_activity.append({
            "type": "rewrite",
            "timestamp": rewrite.created_at.isoformat(),
            "description": f"Rewrote email with {rewrite.tone} tone"
        })
    
    for campaign in recent_campaigns:
        recent_activity.append({
            "type": "campaign",
            "timestamp": campaign.created_at.isoformat(),
            "description": f"Created campaign: {campaign.name}"
        })
    
    # Sort by timestamp
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:10]  # Limit to 10 most recent
    
    logger.info(
        f"Retrieved analytics for user {current_user.id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {
        "usage": {
            "total_rewrites": total_rewrites,
            "rewrites_today": rewrites_today,
            "rewrites_this_week": rewrites_this_week,
            "rewrites_this_month": rewrites_this_month,
            "daily_limit": daily_limit,
            "remaining_today": remaining_today,
            "plan": current_user.subscription_plan
        },
        "campaigns": {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_recipients": total_recipients,
            "sent_emails": sent_emails,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "reply_rate": round(reply_rate, 2)
        },
        "recent_activity": recent_activity
    }

