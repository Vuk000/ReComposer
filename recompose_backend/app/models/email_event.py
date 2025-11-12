# --- Email Event Model ---
"""
EmailEvent model for tracking email events (opens, replies).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class EventType(str, enum.Enum):
    """Email event type enumeration."""
    OPEN = "OPEN"
    REPLY = "REPLY"


class EmailEvent(Base):
    """EmailEvent model for detailed event logging and analytics."""
    
    __tablename__ = "email_events"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    campaign_recipient_id = Column(Integer, ForeignKey("campaign_recipients.id"), nullable=False, index=True)
    
    # --- Event Information ---
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_metadata = Column(JSON, nullable=True)  # Additional event data (IP address, user agent, etc.)
    
    # --- Relationships ---
    campaign_recipient = relationship("CampaignRecipient", back_populates="email_events")

