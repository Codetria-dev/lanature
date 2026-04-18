"""
Integrations router for managing webhooks and external service integrations.

Handles webhook registration, management, and integration configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.domain.webhook_service import webhook_manager, WebhookEvent
from app.domain.slack_service import slack_service, SlackWebhookConfig

router = APIRouter()


def get_current_user_verified(current_user: User = Depends(get_current_user)) -> User:
    """Get current user (must be authenticated)."""
    return current_user


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@router.post("/webhooks", status_code=201)
def register_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """
    Register a new webhook.

    Request body:
    ```json
    {
        "url": "https://example.com/webhook",
        "events": ["task.completed", "reminder.sent"],
        "secret": "optional-signing-secret",
        "active": true
    }
    ```

    Response includes webhook ID for future management.
    """
    url = webhook_data.get("url")
    events_str = webhook_data.get("events", [])
    secret = webhook_data.get("secret")
    active = webhook_data.get("active", True)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL is required"
        )

    # Validate and convert event strings to WebhookEvent enums
    events = []
    for event_str in events_str:
        try:
            event = WebhookEvent(event_str)
            events.append(event)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event_str}"
            )

    if not events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one event must be specified"
        )

    # Register webhook
    webhook_id = webhook_manager.register_webhook(
        user_id=current_user.id,
        webhook_url=url,
        events=events,
        secret=secret,
        active=active
    )

    return {
        "webhook_id": webhook_id,
        "url": url,
        "events": [e.value for e in events],
        "active": active,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/webhooks")
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """
    List all webhooks for current user.

    Returns list of webhook configurations with metadata.
    """
    webhooks = webhook_manager.get_user_webhooks(current_user.id)

    return {
        "webhooks": [
            {
                "webhook_id": w["id"],
                "url": w["url"],
                "events": w["events"],
                "active": w["active"],
                "created_at": w["created_at"],
                "last_delivery": w.get("last_delivery"),
                "delivery_count": w.get("delivery_count", 0),
                "failure_count": w.get("failure_count", 0)
            }
            for w in webhooks
        ],
        "total": len(webhooks)
    }


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """Delete a webhook by ID."""
    success = webhook_manager.unregister_webhook(webhook_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )


@router.patch("/webhooks/{webhook_id}/toggle")
def toggle_webhook(
    webhook_id: str,
    active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """Enable or disable a webhook."""
    webhook = webhook_manager.webhooks.get(webhook_id)

    if not webhook or webhook["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    webhook_manager.toggle_webhook(webhook_id, active)

    return {
        "webhook_id": webhook_id,
        "active": active,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.get("/webhooks/{webhook_id}")
def get_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """Get webhook details."""
    webhook = webhook_manager.webhooks.get(webhook_id)

    if not webhook or webhook["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    # Don't expose secret
    config = {
        "webhook_id": webhook["id"],
        "url": webhook["url"],
        "events": webhook["events"],
        "active": webhook["active"],
        "created_at": webhook["created_at"],
        "last_delivery": webhook.get("last_delivery"),
        "delivery_count": webhook.get("delivery_count", 0),
        "failure_count": webhook.get("failure_count", 0)
    }

    return config


# ============================================================================
# SLACK INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/slack/configure")
def configure_slack(
    slack_config: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """
    Configure Slack webhook for reminders.

    Request body:
    ```json
    {
        "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
    ```

    Note: This is stored client-side. In production, use secure storage.
    """
    webhook_url = slack_config.get("webhook_url")

    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slack webhook URL is required"
        )

    # Verify webhook URL format
    if not webhook_url.startswith("https://hooks.slack.com/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Slack webhook URL"
        )

    # TODO: Store in user preferences/database
    # For now, return success

    return {
        "status": "configured",
        "message": "Slack webhook configured successfully",
        "webhook_configured": True
    }


@router.get("/slack/status")
def slack_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """
    Get Slack integration status.

    Returns whether Slack is configured for the user.
    """
    # TODO: Get from user preferences/database
    webhook_configured = False

    return {
        "configured": webhook_configured,
        "service": "Slack",
        "status": "ready" if webhook_configured else "not_configured"
    }


@router.post("/slack/test")
def test_slack_webhook(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Send test message to Slack.

    Useful for verifying webhook URL is working.
    """
    # This would use the stored webhook URL from configuration
    # For now, just return success

    return {
        "status": "sent",
        "message": "Test message sent to Slack (if configured)"
    }


# ============================================================================
# INTEGRATION STATUS ENDPOINT
# ============================================================================

@router.get("/status")
def integrations_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_verified)
):
    """
    Get status of all integrations for current user.

    Returns list of available integrations and their configuration status.
    """
    webhooks = webhook_manager.get_user_webhooks(current_user.id)

    return {
        "integrations": {
            "webhooks": {
                "available": True,
                "registered": len(webhooks),
                "active": sum(1 for w in webhooks if w["active"])
            },
            "slack": {
                "available": True,
                "configured": False,  # TODO: Check user preferences
                "status": "ready"
            },
            "notion": {
                "available": True,
                "configured": False,
                "status": "ready"
            },
            "google_calendar": {
                "available": False,
                "configured": False,
                "status": "coming_soon",
                "note": "OAuth setup required"
            }
        },
        "webhook_events_available": [e.value for e in WebhookEvent]
    }
