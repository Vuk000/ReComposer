# --- Campaign Recipient Model ---
"""
CampaignRecipient model for tracking contacts in campaigns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db import Base
import enum
import uuid


class RecipientStatus(str, enum.Enum):
    """Recipient status enumeration."""
    PENDING = "Pending"
    SENT = "Sent"
    REPLIED = "Replied"
    BOUNCED = "Bounced"
    FAILED = "Failed"
    SKIPPED = "Skipped"


class CampaignRecipient(Base):
    """CampaignRecipient model tracking individual contacts in campaigns."""
    
    __tablename__ = "campaign_recipients"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Keys ---
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    
    # --- Status Tracking ---
    current_step = Column(Integer, default=0, nullable=False)  # Which step was last sent (0 = none sent yet)
    status = Column(SQLEnum(RecipientStatus), default=RecipientStatus.PENDING, nullable=False, index=True)
    
    # --- Scheduling ---
    last_sent_at = Column(DateTime, nullable=True)
    next_send_at = Column(DateTime, nullable=True, index=True)  # Critical for scheduling queries
    
    # --- Tracking ---
    tracking_id = Column(String, unique=True, nullable=True, index=True)  # UUID for open tracking
    sent_message_id = Column(String, nullable=True)  # Provider message ID (Gmail/Outlook/SMTP)
    open_count = Column(Integer, default=0, nullable=False)
    reply_detected_at = Column(DateTime, nullable=True)
    
    # --- Error Handling ---
    error_message = Column(Text, nullable=True)
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    
    # --- Relationships ---
    campaign = relationship("Campaign", back_populates="campaign_recipients")
    contact = relationship("Contact", back_populates="campaign_recipients")
    email_events = relationship("EmailEvent", back_populates="campaign_recipient", cascade="all, delete-orphan")
    
    def generate_tracking_id(self):
        """Generate a unique tracking ID for this recipient."""
        if not self.tracking_id:
            self.tracking_id = str(uuid.uuid4())
        return self.tracking_id

