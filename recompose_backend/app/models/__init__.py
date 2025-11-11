# --- Models Package ---
"""
Export all models for easy importing.
"""

from app.models.user import User
from app.models.rewrite import RewriteLog
from app.models.contact import Contact
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_email import CampaignEmail
from app.models.campaign_recipient import CampaignRecipient, RecipientStatus
from app.models.email_event import EmailEvent, EventType
from app.models.email_account import EmailAccount, EmailProvider

__all__ = [
    "User",
    "RewriteLog",
    "Contact",
    "Campaign",
    "CampaignStatus",
    "CampaignEmail",
    "CampaignRecipient",
    "RecipientStatus",
    "EmailEvent",
    "EventType",
    "EmailAccount",
    "EmailProvider",
]

