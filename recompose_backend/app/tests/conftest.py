# --- Shared Test Fixtures ---
"""
Shared pytest fixtures for all tests.
"""

import pytest
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.db import get_db, Base

# --- Test Setup ---
# Set OPENAI_API_KEY for tests (required by endpoint validation)
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
# Disable rate limiting in tests
os.environ["RATE_LIMIT_ENABLED"] = "false"

# Reload settings to pick up the environment variable
import importlib
from app import config
importlib.reload(config)
# Also reload rewrite router to get updated OpenAI client
from app.routers import rewrite
importlib.reload(rewrite)
# Reload main app to pick up updated settings for middleware
from app import main
importlib.reload(main)

# --- Test Database Configuration ---
# Use in-memory SQLite for tests (no PostgreSQL required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False}  # SQLite specific
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# --- Test Database Setup ---
@pytest.fixture(scope="function", autouse=True)
async def db_session():
    """Create a test database session with in-memory SQLite."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client with database override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

