# --- Authentication Tests ---
"""
Tests for authentication endpoints (signup, login, JWT token generation).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user import User
from app.db import get_db, Base, engine
from app.core.security import verify_password, create_access_token, decode_access_token


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


# --- Signup Tests ---
@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful user signup."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    """Test signup with duplicate email fails."""
    # Create first user
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Try to create duplicate
    response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "anotherpassword"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient, db_session: AsyncSession):
    """Test signup with invalid email format."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "not-an-email",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 422


# --- Login Tests ---
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful login returns JWT token."""
    # Create user first
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login
    response = await client.post(
        "/auth/login",
        data={
            "username": "test@example.com",  # OAuth2 uses 'username' for email
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token is valid
    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert "sub" in payload


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, db_session: AsyncSession):
    """Test login with invalid credentials fails."""
    # Create user first
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Try login with wrong password
    response = await client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient, db_session: AsyncSession):
    """Test login with non-existent user fails."""
    response = await client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    
    assert response.status_code == 401


# --- JWT Token Tests ---
@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db_session: AsyncSession):
    """Test getting current user with valid token."""
    # Create user and login
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token fails."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test getting current user without token fails."""
    response = await client.get("/auth/me")
    
    assert response.status_code == 401

