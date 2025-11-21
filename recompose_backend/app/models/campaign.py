# --- Campaign Model ---
"""
Campaign model for email campaign definitions.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration."""
    DRAFT = "Draft"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Campaign(Base):
    """Campaign model storing email campaign definitions."""
    
    __tablename__ = "campaigns"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # --- Campaign Information ---
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    launched_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    
    # --- Relationships ---
    user = relationship("User", back_populates="campaigns")
    campaign_emails = relationship("CampaignEmail", back_populates="campaign", cascade="all, delete-orphan", order_by="CampaignEmail.step_number")
    campaign_recipients = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")

