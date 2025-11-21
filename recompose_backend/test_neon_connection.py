#!/usr/bin/env python3
"""
Test Neon PostgreSQL connection
"""

import asyncio
import asyncpg
from app.config import settings

async def test_connection():
    """Test direct connection to Neon PostgreSQL."""
    print("=" * 70)
    print("Testing Neon PostgreSQL Connection")
    print("=" * 70)
    print()
    
    # Extract connection details from DATABASE_URL
    db_url = settings.DATABASE_URL
    print(f"DATABASE_URL: {db_url[:50]}...")
    print()
    
    try:
        # Try to connect
        print("Attempting connection...")
        conn = await asyncpg.connect(db_url.replace("postgresql+asyncpg://", "postgresql://"))
        
        # Test query
        version = await conn.fetchval('SELECT version()')
        print("✅ Connection successful!")
        print(f"PostgreSQL version: {version[:80]}...")
        
        # Check tables
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        print(f"\n✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)

