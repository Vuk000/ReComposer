# --- Rewrite Log Model ---
"""
RewriteLog model for tracking email rewrites and usage analytics.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from app.db import Base


class RewriteLog(Base):
    """Log model for tracking email rewrites with analytics data."""
    
    __tablename__ = "rewrite_logs"
    
    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # --- Email Content ---
    original_email = Column(Text, nullable=False)  # Original email text submitted by user
    rewritten_email = Column(Text, nullable=False)  # Rewritten email text from AI
    
    # --- Rewrite Metadata ---
    tone = Column(String, nullable=False)  # friendly, professional, persuasive
    word_count = Column(Integer, nullable=False)  # Word count of rewritten email
    token_used = Column(BigInteger, nullable=False, default=0)  # OpenAI tokens consumed
    
    # --- Timestamps ---
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # --- Relationships ---
    user = relationship("User", back_populates="rewrite_logs")

