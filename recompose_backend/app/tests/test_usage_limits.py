# --- Usage Limits Tests ---
"""
Tests for daily usage limits functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.core.security import get_password_hash


@pytest.fixture(scope="function")
async def authenticated_user(client: AsyncClient, db_session: AsyncSession):
    """Create and authenticate a test user."""
    # Create user
    signup_response = await client.post(
        "/api/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login to get token (using JSON body)
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    token = login_response.json()["access_token"]
    return token


@pytest.fixture(scope="function")
async def pro_user(client: AsyncClient, db_session: AsyncSession):
    """Create and authenticate a pro plan user."""
    # Create user
    signup_response = await client.post(
        "/api/auth/signup",
        json={
            "email": "pro@example.com",
            "password": "testpassword123"
        }
    )
    
    # Get user and update to pro plan
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "pro@example.com")
    )
    user = result.scalar_one_or_none()
    user.subscription_plan = "pro"
    await db_session.commit()
    
    # Login to get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "pro@example.com",
            "password": "testpassword123"
        }
    )
    
    token = login_response.json()["access_token"]
    return token


# --- Mock OpenAI Response ---
def create_mock_openai_response(rewritten_text: str, tokens_used: int = 100):
    """Create a mock OpenAI API response."""
    mock_response = AsyncMock()
    mock_choice = AsyncMock()
    mock_choice.message.content = rewritten_text
    mock_response.choices = [mock_choice]
    
    mock_usage = AsyncMock()
    mock_usage.total_tokens = tokens_used
    mock_usage.model_dump = lambda: {"total_tokens": tokens_used}
    
    mock_response.usage = mock_usage
    return mock_response


# --- Usage Endpoint Tests ---
@pytest.mark.asyncio
async def test_get_usage_free_user(
    client: AsyncClient,
    authenticated_user: str
):
    """Test usage endpoint for free user."""
    response = await client.get(
        "/api/rewrite/usage",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "used" in data
    assert "limit" in data
    assert "remaining" in data
    assert "plan" in data
    assert data["plan"] == "standard"  # New users default to "standard" plan
    assert data["limit"] == 20
    assert data["used"] == 0
    assert data["remaining"] == 20


@pytest.mark.asyncio
async def test_get_usage_pro_user(
    client: AsyncClient,
    pro_user: str
):
    """Test usage endpoint for pro user."""
    response = await client.get(
        "/api/rewrite/usage",
        headers={"Authorization": f"Bearer {pro_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "pro"
    assert data["limit"] == 1000  # PRO_PLAN_DAILY_LIMIT
    assert data["used"] == 0
    assert data["remaining"] == 1000


@pytest.mark.asyncio
async def test_usage_updates_after_rewrite(
    client: AsyncClient,
    authenticated_user: str
):
    """Test that usage count updates after rewrite."""
    # Make a rewrite
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = create_mock_openai_response("Rewritten email", 100)
        
        await client.post(
            "/api/rewrite",
            json={
                "email_text": "Original email",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    # Check usage
    response = await client.get(
        "/api/rewrite/usage",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["used"] == 1
    assert data["remaining"] == 19


# --- Usage Limit Enforcement Tests ---
@pytest.mark.asyncio
async def test_free_user_limit_enforcement(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test that free users are blocked after reaching daily limit."""
    # Create 20 rewrite logs for the user (simulating limit reached)
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    
    # Create 20 logs since UTC midnight today
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(20):
        log = RewriteLog(
            user_id=user.id,
            original_email=f"Original {i}",
            rewritten_email=f"Rewritten {i}",
            tone="professional",
            word_count=10,
            token_used=100,
            created_at=start_of_day + timedelta(hours=i % 24)  # Spread throughout today
        )
        db_session.add(log)
    await db_session.commit()
    
    # Try to make another rewrite
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = create_mock_openai_response("Should not work", 100)
        
        response = await client.post(
            "/api/rewrite",
            json={
                "email_text": "New email",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    assert response.status_code == 429
    assert "limit" in response.json()["detail"].lower()
    assert "20" in response.json()["detail"]


@pytest.mark.asyncio
async def test_pro_user_no_limit_enforcement(
    client: AsyncClient,
    pro_user: str,
    db_session: AsyncSession
):
    """Test that pro users can exceed free limit."""
    # Create 25 rewrite logs for the pro user
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "pro@example.com")
    )
    user = result.scalar_one_or_none()
    
    # Create 25 logs since UTC midnight today
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(25):
        log = RewriteLog(
            user_id=user.id,
            original_email=f"Original {i}",
            rewritten_email=f"Rewritten {i}",
            tone="professional",
            word_count=10,
            token_used=100,
            created_at=start_of_day + timedelta(hours=i % 24)  # Spread throughout today
        )
        db_session.add(log)
    await db_session.commit()
    
    # Pro user should still be able to rewrite
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = create_mock_openai_response("Should work", 100)
        
        response = await client.post(
            "/api/rewrite",
            json={
                "email_text": "New email",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {pro_user}"}
        )
    
    assert response.status_code == 200
    assert "rewritten_email" in response.json()


@pytest.mark.asyncio
async def test_usage_resets_at_utc_midnight(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test that usage counts only include rewrites from current UTC day (resets at UTC midnight)."""
    # Create a rewrite log from yesterday (before UTC midnight)
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    yesterday_midnight = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)
    
    old_log = RewriteLog(
        user_id=user.id,
        original_email="Old email",
        rewritten_email="Old rewritten",
        tone="professional",
        word_count=10,
        token_used=100,
        created_at=yesterday_midnight  # Yesterday before UTC midnight
    )
    db_session.add(old_log)
    
    # Create a recent rewrite from today (after UTC midnight)
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    recent_log = RewriteLog(
        user_id=user.id,
        original_email="Recent email",
        rewritten_email="Recent rewritten",
        tone="professional",
        word_count=10,
        token_used=100,
        created_at=today_midnight + timedelta(hours=1)  # Today after UTC midnight
    )
    db_session.add(recent_log)
    await db_session.commit()
    
    # Check usage - should only count recent rewrite from today
    response = await client.get(
        "/api/rewrite/usage",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["used"] == 1  # Only the one from today
    assert data["remaining"] == 19


@pytest.mark.asyncio
async def test_usage_endpoint_unauthorized(client: AsyncClient):
    """Test usage endpoint without authentication fails."""
    response = await client.get("/api/rewrite/usage")
    
    assert response.status_code == 401

