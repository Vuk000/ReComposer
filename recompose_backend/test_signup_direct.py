#!/usr/bin/env python3
"""Test signup directly to see detailed errors."""

import asyncio
from app.db import get_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def test_signup():
    """Test user signup directly."""
    from app.db import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if user exists
            result = await session.execute(select(User).where(User.email == "test@example.com"))
            existing = result.scalar_one_or_none()
            if existing:
                print("User already exists, deleting...")
                await session.delete(existing)
                await session.commit()
            
            # Create new user
            print("Creating user...")
            hashed_password = get_password_hash("TestPassword123")
            new_user = User(
                email="test@example.com",
                hashed_password=hashed_password
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            print(f"✓ User created: {new_user.email}, ID: {new_user.id}")
            print(f"  Subscription plan: {new_user.subscription_plan}")
            print(f"  Subscription status: {new_user.subscription_status}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(test_signup())

