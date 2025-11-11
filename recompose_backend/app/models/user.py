# --- User Model ---
"""
User model for authentication and user management.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    """User model storing email and hashed password."""
    
    __tablename__ = "users"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- User Credentials ---
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # --- Subscription Fields ---
    subscription_plan = Column(String, default="standard", nullable=False)  # standard ($14.99/month), pro ($49.99/month)
    subscription_status = Column(String, default="active", nullable=False)  # active, cancelled, past_due
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)  # Optional trial period end date
    
    # --- Relationships ---
    rewrite_logs = relationship("RewriteLog", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    email_accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")

