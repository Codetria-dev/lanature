"""
Tests for integrations and webhooks functionality.

Tests webhook registration, management, and event delivery.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.auth import get_password_hash, create_access_token
from app.database import get_db
from app.domain.webhook_service import webhook_manager, WebhookEvent, WebhookPayload


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client(db):
    """FastAPI test client with overridden database."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    """Create user for testing."""
    user = User(
        name="Test User",
        email="webhook_test@test.com",
        password_hash=get_password_hash("TestPass@123"),
        is_superuser=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(user):
    """Create JWT token for user."""
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def user_headers(user_token):
    """Authorization headers for user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(autouse=True)
def clear_webhooks():
    """Clear webhook registry before each test."""
    webhook_manager.webhooks.clear()
    webhook_manager.user_webhooks.clear()
    yield
    webhook_manager.webhooks.clear()
    webhook_manager.user_webhooks.clear()


# ============================================================================
# WEBHOOK REGISTRATION TESTS
# ============================================================================

def test_register_webhook(client, user_headers, user):
    """
    Test registering a new webhook.

    POST /api/v1/integrations/webhooks should:
    - Accept webhook URL and events
    - Return webhook ID
    - Register webhook with user
    """
    response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook",
            "events": ["task.completed", "pet.created"],
            "secret": "test-secret"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "webhook_id" in data
    assert data["url"] == "https://example.com/webhook"
    assert set(data["events"]) == {"task.completed", "pet.created"}
    assert data["active"] is True


def test_register_webhook_without_url(client, user_headers):
    """Test registering webhook without URL returns error."""
    response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={"events": ["task.completed"]}
    )

    assert response.status_code == 400
    assert "URL is required" in response.json()["detail"]


def test_register_webhook_without_events(client, user_headers):
    """Test registering webhook without events returns error."""
    response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={"url": "https://example.com/webhook"}
    )

    assert response.status_code == 400
    assert "event" in response.json()["detail"].lower()


def test_register_webhook_invalid_event(client, user_headers):
    """Test registering webhook with invalid event type."""
    response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook",
            "events": ["invalid_event"]
        }
    )

    assert response.status_code == 400
    assert "Invalid event type" in response.json()["detail"]


# ============================================================================
# WEBHOOK LISTING TESTS
# ============================================================================

def test_list_webhooks_empty(client, user_headers):
    """Test listing webhooks when none exist."""
    response = client.get(
        "/api/v1/integrations/webhooks",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["webhooks"]) == 0


def test_list_webhooks_with_registered(client, user_headers, user):
    """Test listing webhooks shows registered webhooks."""
    # Register a webhook
    client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook1",
            "events": ["task.completed"]
        }
    )

    # Register another webhook
    client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook2",
            "events": ["pet.created", "pet.updated"]
        }
    )

    # List webhooks
    response = client.get(
        "/api/v1/integrations/webhooks",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["webhooks"]) == 2

    urls = {w["url"] for w in data["webhooks"]}
    assert "https://example.com/webhook1" in urls
    assert "https://example.com/webhook2" in urls


# ============================================================================
# WEBHOOK MANAGEMENT TESTS
# ============================================================================

def test_toggle_webhook(client, user_headers, user):
    """Test enabling/disabling a webhook."""
    # Register webhook
    register_response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook",
            "events": ["task.completed"]
        }
    )
    webhook_id = register_response.json()["webhook_id"]

    # Disable webhook
    response = client.patch(
        f"/api/v1/integrations/webhooks/{webhook_id}/toggle",
        headers=user_headers,
        params={"active": False}
    )

    assert response.status_code == 200
    assert response.json()["active"] is False

    # Verify webhook is disabled
    list_response = client.get(
        "/api/v1/integrations/webhooks",
        headers=user_headers
    )
    webhook = list_response.json()["webhooks"][0]
    assert webhook["active"] is False

    # Enable webhook
    response = client.patch(
        f"/api/v1/integrations/webhooks/{webhook_id}/toggle",
        headers=user_headers,
        params={"active": True}
    )

    assert response.status_code == 200
    assert response.json()["active"] is True


def test_delete_webhook(client, user_headers, user):
    """Test deleting a webhook."""
    # Register webhook
    register_response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook",
            "events": ["task.completed"]
        }
    )
    webhook_id = register_response.json()["webhook_id"]

    # Verify webhook exists
    list_response = client.get(
        "/api/v1/integrations/webhooks",
        headers=user_headers
    )
    assert list_response.json()["total"] == 1

    # Delete webhook
    response = client.delete(
        f"/api/v1/integrations/webhooks/{webhook_id}",
        headers=user_headers
    )

    assert response.status_code == 204

    # Verify webhook is deleted
    list_response = client.get(
        "/api/v1/integrations/webhooks",
        headers=user_headers
    )
    assert list_response.json()["total"] == 0


def test_get_webhook_details(client, user_headers, user):
    """Test getting webhook details."""
    # Register webhook
    register_response = client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook",
            "events": ["task.completed", "reminder.sent"]
        }
    )
    webhook_id = register_response.json()["webhook_id"]

    # Get webhook details
    response = client.get(
        f"/api/v1/integrations/webhooks/{webhook_id}",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["webhook_id"] == webhook_id
    assert data["url"] == "https://example.com/webhook"
    assert set(data["events"]) == {"task.completed", "reminder.sent"}


def test_delete_nonexistent_webhook(client, user_headers):
    """Test deleting non-existent webhook returns error."""
    response = client.delete(
        "/api/v1/integrations/webhooks/nonexistent-id",
        headers=user_headers
    )

    assert response.status_code == 404


# ============================================================================
# SLACK INTEGRATION TESTS
# ============================================================================

def test_configure_slack(client, user_headers):
    """Test configuring Slack webhook."""
    response = client.post(
        "/api/v1/integrations/slack/configure",
        headers=user_headers,
        json={
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "configured"
    assert data["webhook_configured"] is True


def test_configure_slack_invalid_url(client, user_headers):
    """Test configuring Slack with invalid webhook URL."""
    response = client.post(
        "/api/v1/integrations/slack/configure",
        headers=user_headers,
        json={"webhook_url": "https://example.com/webhook"}
    )

    assert response.status_code == 400
    assert "Invalid Slack webhook URL" in response.json()["detail"]


def test_slack_status(client, user_headers):
    """Test getting Slack integration status."""
    response = client.get(
        "/api/v1/integrations/slack/status",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert data["service"] == "Slack"


# ============================================================================
# INTEGRATIONS STATUS TESTS
# ============================================================================

def test_integrations_status(client, user_headers, user):
    """Test getting all integrations status."""
    # Register some webhooks
    client.post(
        "/api/v1/integrations/webhooks",
        headers=user_headers,
        json={
            "url": "https://example.com/webhook1",
            "events": ["task.completed"]
        }
    )

    response = client.get(
        "/api/v1/integrations/status",
        headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "integrations" in data
    assert "webhook_events_available" in data
    assert "webhooks" in data["integrations"]
    assert data["integrations"]["webhooks"]["available"] is True
    assert data["integrations"]["webhooks"]["registered"] == 1
    assert "slack" in data["integrations"]


def test_webhook_events_list(client, user_headers):
    """Test that all webhook events are listed."""
    response = client.get(
        "/api/v1/integrations/status",
        headers=user_headers
    )

    assert response.status_code == 200
    events = response.json()["webhook_events_available"]

    # Verify expected events are present
    expected_events = [
        "task.completed", "task.created", "task.deleted",
        "pet.created", "pet.updated", "pet.deleted",
        "reminder.sent", "reminder.missed",
        "user.registered", "user.deleted"
    ]

    for event in expected_events:
        assert event in events


# ============================================================================
# WEBHOOK PAYLOAD TESTS
# ============================================================================

def test_webhook_payload_serialization():
    """Test WebhookPayload serialization."""
    payload = WebhookPayload(
        event=WebhookEvent.TASK_COMPLETED,
        user_id=123,
        data={
            "task_id": 456,
            "pet_name": "Fluffy",
            "completion_time": "2026-04-18T12:30:00"
        }
    )

    data = payload.to_dict()

    assert data["event"] == "task.completed"
    assert data["user_id"] == 123
    assert data["data"]["task_id"] == 456
    assert "event_id" in data
    assert "timestamp" in data


def test_webhook_payload_signing():
    """Test webhook payload HMAC signing."""
    payload = WebhookPayload(
        event=WebhookEvent.TASK_COMPLETED,
        user_id=123,
        data={"task_id": 456}
    )

    signature = payload.sign("secret")

    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA256 hex is 64 chars
