# --- Contact Model ---
"""
Contact model for storing user contacts/prospects.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db import Base


class Contact(Base):
    """Contact model storing prospect information."""
    
    __tablename__ = "contacts"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # --- Contact Information ---
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)
    
    # --- Relationships ---
    user = relationship("User", back_populates="contacts")
    campaign_recipients = relationship("CampaignRecipient", back_populates="contact", cascade="all, delete-orphan")
    
    # --- Indexes ---
    __table_args__ = (
        Index('ix_contacts_user_email', 'user_id', 'email'),  # Composite index for deduplication
    )

