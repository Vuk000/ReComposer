# --- Email Account Model ---
"""
EmailAccount model for user's connected email accounts.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class EmailProvider(str, enum.Enum):
    """Email provider enumeration."""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    SMTP = "smtp"
    BREVO = "brevo"


class EmailAccount(Base):
    """EmailAccount model storing user's connected email accounts."""
    
    __tablename__ = "email_accounts"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # --- Account Information ---
    provider = Column(SQLEnum(EmailProvider), nullable=False, index=True)
    email_address = Column(String, nullable=False)
    
    # --- OAuth Tokens (encrypted) ---
    encrypted_oauth_token = Column(String, nullable=True)  # Encrypted access token
    encrypted_refresh_token = Column(String, nullable=True)  # Encrypted refresh token
    
    # --- SMTP Configuration (JSON) ---
    # Structure: {"host": str, "port": int, "username": str, "encrypted_password": str, "use_tls": bool}
    smtp_config = Column(JSON, nullable=True)
    
    # --- Status ---
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # --- Timestamps ---
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)
    
    # --- Relationships ---
    user = relationship("User", back_populates="email_accounts")

