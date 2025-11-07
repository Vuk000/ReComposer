# --- User Model ---
"""
User model for authentication and user management.
"""

from datetime import datetime
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # --- Relationships ---
    rewrite_logs = relationship("RewriteLog", back_populates="user", cascade="all, delete-orphan")

