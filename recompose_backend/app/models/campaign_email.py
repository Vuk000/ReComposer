# --- Campaign Email Model ---
"""
CampaignEmail model for email templates/steps in campaign sequences.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class CampaignEmail(Base):
    """CampaignEmail model storing email templates for campaign steps."""
    
    __tablename__ = "campaign_emails"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # --- Email Template Information ---
    step_number = Column(Integer, nullable=False)  # 1 = initial, 2+ = follow-ups
    subject = Column(String, nullable=False)
    body_template = Column(Text, nullable=False)  # Template with placeholders like {{Name}}, {{Company}}
    delay_days = Column(Integer, default=0, nullable=False)  # Days to wait before sending this step
    delay_hours = Column(Integer, default=0, nullable=False)  # Additional hours for precise timing
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    
    # --- Relationships ---
    campaign = relationship("Campaign", back_populates="campaign_emails")
    
    # --- Indexes ---
    __table_args__ = (
        # Ensure step_number is unique per campaign
        # Note: This will be enforced at application level or via unique constraint
    )

