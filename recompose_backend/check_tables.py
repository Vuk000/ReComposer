#!/usr/bin/env python3
"""Check database tables structure."""

import asyncio
from sqlalchemy import inspect, text
from app.db import engine, Base

async def check_tables():
    """Check if tables exist and their structure."""
    async with engine.connect() as conn:
        # Check tables
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print(f"Tables found: {tables}")
        
        # Check users table structure
        if 'users' in tables:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = result.fetchall()
            print(f"\nUsers table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("\nUsers table not found!")
            
        # Recreate all tables
        print("\nRecreating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tables recreated")

if __name__ == "__main__":
    asyncio.run(check_tables())

