# --- Rewrite Tests ---
"""
Tests for email rewrite endpoint with mocked OpenAI API.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from sqlalchemy import select, desc
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.db import get_db, Base, engine
from app.core.security import get_password_hash


# --- Test Database Setup ---
@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
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


@pytest.fixture(scope="function")
async def authenticated_user(client: AsyncClient, db_session: AsyncSession):
    """Create and authenticate a test user."""
    # Create user
    signup_response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login to get token
    login_response = await client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
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
    mock_response.usage = mock_usage
    return mock_response


# --- Rewrite Endpoint Tests ---
@pytest.mark.asyncio
async def test_rewrite_success(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test successful email rewrite."""
    original_text = "Hey, I need this done ASAP!"
    rewritten_text = "Hello, I would appreciate it if you could complete this task as soon as possible."
    
    with patch("app.routers.rewrite.openai_client.chat.completions.create") as mock_create:
        mock_create.return_value = create_mock_openai_response(rewritten_text, 150)
        
        response = await client.post(
            "/rewrite",
            json={
                "email_text": original_text,
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "rewritten_email" in data
    assert data["rewritten_email"] == rewritten_text
    
    # Verify rewrite was logged
    from sqlalchemy import select
    result = await db_session.execute(
        select(RewriteLog).where(RewriteLog.tone == "professional")
    )
    logs = result.scalars().all()
    assert len(logs) > 0


@pytest.mark.asyncio
async def test_rewrite_different_tones(
    client: AsyncClient,
    authenticated_user: str
):
    """Test rewrite with different tone options."""
    tones = ["friendly", "professional", "persuasive"]
    
    for tone in tones:
        with patch("app.routers.rewrite.openai_client.chat.completions.create") as mock_create:
            mock_create.return_value = create_mock_openai_response(f"Rewritten with {tone} tone")
            
            response = await client.post(
                "/rewrite",
                json={
                    "email_text": "Test email",
                    "tone": tone
                },
                headers={"Authorization": f"Bearer {authenticated_user}"}
            )
        
        assert response.status_code == 200
        assert "rewritten_email" in response.json()


@pytest.mark.asyncio
async def test_rewrite_invalid_tone(
    client: AsyncClient,
    authenticated_user: str
):
    """Test rewrite with invalid tone fails."""
    response = await client.post(
        "/rewrite",
        json={
            "email_text": "Test email",
            "tone": "invalid_tone"
        },
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 400
    assert "tone" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rewrite_empty_email(
    client: AsyncClient,
    authenticated_user: str
):
    """Test rewrite with empty email text fails."""
    response = await client.post(
        "/rewrite",
        json={
            "email_text": "",
            "tone": "professional"
        },
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rewrite_unauthorized(client: AsyncClient):
    """Test rewrite without authentication fails."""
    response = await client.post(
        "/rewrite",
        json={
            "email_text": "Test email",
            "tone": "professional"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rewrite_openai_error(
    client: AsyncClient,
    authenticated_user: str
):
    """Test rewrite handles OpenAI API errors gracefully."""
    with patch("app.routers.rewrite.openai_client.chat.completions.create") as mock_create:
        mock_create.side_effect = Exception("OpenAI API Error")
        
        response = await client.post(
            "/rewrite",
            json={
                "email_text": "Test email",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rewrite_logs_usage(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test that rewrite logs token usage and word count."""
    rewritten_text = "This is a rewritten email with multiple words for testing purposes."
    tokens_used = 200
    
    with patch("app.routers.rewrite.openai_client.chat.completions.create") as mock_create:
        mock_create.return_value = create_mock_openai_response(rewritten_text, tokens_used)
        
        await client.post(
            "/rewrite",
            json={
                "email_text": "Original email",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    # Verify log was created with correct data
    from sqlalchemy import select, desc
    result = await db_session.execute(
        select(RewriteLog).order_by(desc(RewriteLog.created_at)).limit(1)
    )
    log = result.scalar_one_or_none()
    
    assert log is not None
    assert log.tone == "professional"
    assert log.token_used == tokens_used
    assert log.word_count > 0

