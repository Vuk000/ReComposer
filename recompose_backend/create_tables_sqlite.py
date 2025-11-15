#!/usr/bin/env python3
"""
Create database tables using SQLite for development/testing.
This allows testing without PostgreSQL installed.
"""

import asyncio
from app.db import Base, engine
# Import all models to ensure they're registered with Base.metadata
from app.models import (
    User, RewriteLog, Contact, Campaign, CampaignEmail,
    CampaignRecipient, EmailEvent, EmailAccount
)

async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())

