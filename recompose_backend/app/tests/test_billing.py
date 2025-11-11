# --- Billing Tests ---
"""
Tests for Stripe billing integration.
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


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
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    token = login_response.json()["access_token"]
    return token


@pytest.fixture(autouse=True)
def enable_billing(monkeypatch):
    """Enable billing for all tests."""
    monkeypatch.setenv("BILLING_ENABLED", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")


# --- Subscription Status Tests ---
@pytest.mark.asyncio
async def test_get_subscription_status_free_user(
    client: AsyncClient,
    authenticated_user: str
):
    """Test getting subscription status for free user."""
    response = await client.get(
        "/billing/status",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "free"
    assert data["status"] == "active"
    assert data["customer_id"] is None
    assert data["subscription_id"] is None


@pytest.mark.asyncio
async def test_get_subscription_status_unauthorized(client: AsyncClient):
    """Test subscription status endpoint without authentication fails."""
    response = await client.get("/billing/status")
    
    assert response.status_code == 401


# --- Subscribe Endpoint Tests ---
@pytest.mark.asyncio
async def test_subscribe_success(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test successful subscription creation."""
    # Mock Stripe API calls
    mock_customer = MagicMock()
    mock_customer.id = "cus_test123"
    
    mock_subscription = MagicMock()
    mock_subscription.id = "sub_test123"
    mock_subscription.status = "active"
    
    with patch("app.routers.billing.stripe.Customer.create", return_value=mock_customer), \
         patch("app.routers.billing.stripe.Subscription.create", return_value=mock_subscription):
        
        response = await client.post(
            "/billing/subscribe",
            json={
                "plan": "pro"
            },
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "pro"
    assert data["status"] == "active"
    assert data["customer_id"] == "cus_test123"
    assert data["subscription_id"] == "sub_test123"
    
    # Verify user was updated in database
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    assert user.subscription_plan == "pro"
    assert user.stripe_customer_id == "cus_test123"
    assert user.stripe_subscription_id == "sub_test123"


@pytest.mark.asyncio
async def test_subscribe_invalid_plan(
    client: AsyncClient,
    authenticated_user: str
):
    """Test subscription with invalid plan fails."""
    response = await client.post(
        "/billing/subscribe",
        json={
            "plan": "invalid_plan"
        },
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 400
    assert "plan" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_subscribe_billing_disabled(
    client: AsyncClient,
    authenticated_user: str,
    monkeypatch
):
    """Test subscription when billing is disabled."""
    monkeypatch.setenv("BILLING_ENABLED", "false")
    
    response = await client.post(
        "/billing/subscribe",
        json={
            "plan": "pro"
        },
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_subscribe_unauthorized(client: AsyncClient):
    """Test subscription endpoint without authentication fails."""
    response = await client.post(
        "/billing/subscribe",
        json={
            "plan": "pro"
        }
    )
    
    assert response.status_code == 401


# --- Cancel Subscription Tests ---
@pytest.mark.asyncio
async def test_cancel_subscription_success(
    client: AsyncClient,
    authenticated_user: str,
    db_session: AsyncSession
):
    """Test successful subscription cancellation."""
    # First, set up user with subscription
    from sqlalchemy import select
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    user.stripe_subscription_id = "sub_test123"
    user.subscription_plan = "pro"
    user.subscription_status = "active"
    await db_session.commit()
    
    # Mock Stripe API call
    mock_subscription = MagicMock()
    mock_subscription.status = "active"
    
    with patch("app.routers.billing.stripe.Subscription.modify", return_value=mock_subscription):
        response = await client.post(
            "/billing/cancel",
            headers={"Authorization": f"Bearer {authenticated_user}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "cancelled" in data["message"].lower()
    
    # Verify user status was updated
    await db_session.refresh(user)
    assert user.subscription_status == "cancelled"


@pytest.mark.asyncio
async def test_cancel_no_subscription(
    client: AsyncClient,
    authenticated_user: str
):
    """Test cancellation when user has no subscription."""
    response = await client.post(
        "/billing/cancel",
        headers={"Authorization": f"Bearer {authenticated_user}"}
    )
    
    assert response.status_code == 400
    assert "subscription" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_unauthorized(client: AsyncClient):
    """Test cancel endpoint without authentication fails."""
    response = await client.post("/billing/cancel")
    
    assert response.status_code == 401


# --- Webhook Tests ---
@pytest.mark.asyncio
async def test_webhook_subscription_created(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test webhook handling for subscription.created event."""
    # Create a user with Stripe customer ID
    user = User(
        email="webhook@example.com",
        hashed_password="hashed",
        stripe_customer_id="cus_test123"
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock webhook event
    mock_event = {
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test123",
                "customer": "cus_test123",
                "status": "active",
                "metadata": {
                    "plan": "pro",
                    "user_id": str(user.id)
                }
            }
        }
    }
    
    # Mock Stripe webhook verification
    with patch("app.routers.billing.stripe.Webhook.construct_event", return_value=mock_event):
        response = await client.post(
            "/billing/webhook",
            headers={"stripe-signature": "test_signature"},
            content=b'{"test": "data"}'
        )
    
    assert response.status_code == 200
    
    # Verify user was updated
    await db_session.refresh(user)
    assert user.subscription_plan == "pro"
    assert user.stripe_subscription_id == "sub_test123"
    assert user.subscription_status == "active"


@pytest.mark.asyncio
async def test_webhook_subscription_updated(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test webhook handling for subscription.updated event."""
    # Create a user with subscription
    user = User(
        email="webhook2@example.com",
        hashed_password="hashed",
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        subscription_plan="pro",
        subscription_status="active"
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock webhook event
    mock_event = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_test123",
                "customer": "cus_test123",
                "status": "past_due",
                "metadata": {
                    "plan": "pro",
                    "user_id": str(user.id)
                }
            }
        }
    }
    
    with patch("app.routers.billing.stripe.Webhook.construct_event", return_value=mock_event):
        response = await client.post(
            "/billing/webhook",
            headers={"stripe-signature": "test_signature"},
            content=b'{"test": "data"}'
        )
    
    assert response.status_code == 200
    
    # Verify user status was updated
    await db_session.refresh(user)
    assert user.subscription_status == "past_due"


@pytest.mark.asyncio
async def test_webhook_subscription_deleted(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test webhook handling for subscription.deleted event."""
    # Create a user with subscription
    user = User(
        email="webhook3@example.com",
        hashed_password="hashed",
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        subscription_plan="pro",
        subscription_status="active"
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock webhook event
    mock_event = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_test123",
                "customer": "cus_test123"
            }
        }
    }
    
    with patch("app.routers.billing.stripe.Webhook.construct_event", return_value=mock_event):
        response = await client.post(
            "/billing/webhook",
            headers={"stripe-signature": "test_signature"},
            content=b'{"test": "data"}'
        )
    
    assert response.status_code == 200
    
    # Verify user was downgraded to free
    await db_session.refresh(user)
    assert user.subscription_plan == "free"
    assert user.subscription_status == "cancelled"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(client: AsyncClient):
    """Test webhook with invalid signature fails."""
    import stripe
    
    with patch("app.routers.billing.stripe.Webhook.construct_event") as mock_construct:
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "sig_header"
        )
        
        response = await client.post(
            "/billing/webhook",
            headers={"stripe-signature": "invalid_signature"},
            content=b'{"test": "data"}'
        )
    
    assert response.status_code == 400
    assert "signature" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_webhook_billing_disabled(client: AsyncClient, monkeypatch):
    """Test webhook when billing is disabled."""
    monkeypatch.setenv("BILLING_ENABLED", "false")
    
    response = await client.post(
        "/billing/webhook",
        headers={"stripe-signature": "test_signature"},
        content=b'{"test": "data"}'
    )
    
    assert response.status_code == 503

