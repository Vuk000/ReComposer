# --- Rewrite Tests ---
"""
Tests for email rewrite endpoint with mocked OpenAI API.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.core.security import get_password_hash


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
    
    # Login to get token (using JSON body)
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
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
    
    # Create a proper usage mock with model_dump method
    mock_usage = AsyncMock()
    mock_usage.total_tokens = tokens_used
    # Make model_dump return a dict (not a coroutine)
    mock_usage.model_dump = lambda: {"total_tokens": tokens_used}
    
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
    
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_response = create_mock_openai_response(rewritten_text, 150)
        mock_create.return_value = mock_response
        
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
        with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
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
    
    assert response.status_code == 422  # Validation error
    detail = response.json()["detail"]
    # Check if error mentions tone (could be in any error object)
    assert any("tone" in str(err).lower() for err in detail)


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
    
    assert response.status_code == 422  # Validation error
    detail = response.json()["detail"]
    # Check if error mentions empty, min_length, or email_text validation
    error_str = str(detail).lower()
    assert "empty" in error_str or "min_length" in error_str or "email_text" in error_str


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
    
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_response = create_mock_openai_response(rewritten_text, tokens_used)
        mock_create.return_value = mock_response
        
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
    assert log.original_email == "Original email"
    assert log.rewritten_email == rewritten_text


# --- Get Rewrite Logs Endpoint Tests ---
@pytest.mark.asyncio
async def test_get_logs_success(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test successful retrieval of rewrite logs."""
    original_text = "Test email 1"
    rewritten_text = "Rewritten email 1"
    
    # Create a rewrite to generate a log
    with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_response = create_mock_openai_response(rewritten_text, 100)
        mock_create.return_value = mock_response
        
        await client.post(
            "/rewrite",
            json={
                "email_text": original_text,
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    # Get logs
    response = await client.get(
        "/rewrite/logs",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert len(data["logs"]) == 1
    assert data["total"] == 1
    
    log = data["logs"][0]
    assert log["original_email"] == original_text
    assert log["rewritten_email"] == rewritten_text
    assert log["tone"] == "professional"
    assert "id" in log
    assert "word_count" in log
    assert "token_used" in log
    assert "created_at" in log


@pytest.mark.asyncio
async def test_get_logs_empty(
    client: AsyncClient,
    authenticated_user: str
):
    """Test getting logs when user has no rewrites."""
    response = await client.get(
        "/rewrite/logs",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["logs"] == []
    assert data["total"] == 0
    assert data["limit"] == 20
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_get_logs_pagination(
    client: AsyncClient,
    authenticated_user: str
):
    """Test pagination with limit and offset."""
    # Create multiple rewrites
    for i in range(5):
        with patch("app.routers.rewrite.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = create_mock_openai_response(f"Rewritten {i}", 100)
            
            await client.post(
                "/rewrite",
                json={
                    "email_text": f"Original {i}",
                    "tone": "professional"
                },
                headers={"Authorization": f"Bearer {authenticated_user}"}
            )
    
    # Get first page with limit 2
    response = await client.get(
        "/rewrite/logs?limit=2&offset=0",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    
    # Get second page
    response = await client.get(
        "/rewrite/logs?limit=2&offset=2",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 2


@pytest.mark.asyncio
async def test_get_logs_unauthorized(client: AsyncClient):
    """Test getting logs without authentication fails."""
    response = await client.get("/rewrite/logs")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_logs_user_isolation(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test that users only see their own logs."""
    # Create first user and make a rewrite
    user1_response = await client.post(
        "/auth/signup",
        json={
            "email": "user1@example.com",
            "password": "password123"
        }
    )
    user1_login = await client.post(
        "/auth/login",
        json={
            "email": "user1@example.com",
            "password": "password123"
        }
    )
    user1_token = user1_login.json()["access_token"]
    
    with patch("app.routers.rewrite.openai_client.chat.completions.create") as mock_create:
        mock_create.return_value = create_mock_openai_response("User1 rewrite", 100)
        
        await client.post(
            "/rewrite",
            json={
                "email_text": "User1 original",
                "tone": "professional"
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )
    
    # Create second user
    user2_response = await client.post(
        "/auth/signup",
        json={
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    user2_login = await client.post(
        "/auth/login",
        json={
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    user2_token = user2_login.json()["access_token"]
    
    # User2 should see no logs
    response = await client.get(
        "/rewrite/logs",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["logs"]) == 0

