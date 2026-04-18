"""
Webhook service for integration events.

Manages webhook registration, delivery, and event handling.
Supports external integrations to receive notifications about app events.
"""

import httpx
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import hmac

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types."""
    TASK_COMPLETED = "task.completed"
    TASK_CREATED = "task.created"
    TASK_DELETED = "task.deleted"
    PET_CREATED = "pet.created"
    PET_UPDATED = "pet.updated"
    PET_DELETED = "pet.deleted"
    REMINDER_SENT = "reminder.sent"
    REMINDER_MISSED = "reminder.missed"
    USER_REGISTERED = "user.registered"
    USER_DELETED = "user.deleted"


class WebhookPayload:
    """Represents a webhook payload to be sent."""

    def __init__(self, event: WebhookEvent, user_id: int, data: Dict):
        self.event = event
        self.user_id = user_id
        self.data = data
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "event": self.event.value,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "data": self.data
        }

    def sign(self, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        payload_str = str(self.to_dict()).encode('utf-8')
        return hmac.new(
            secret.encode('utf-8'),
            payload_str,
            hashlib.sha256
        ).hexdigest()


class WebhookService:
    """
    Webhook management and delivery service.

    Features:
    - Register webhooks for specific events
    - Deliver webhook payloads to registered endpoints
    - Signature verification for webhook authenticity
    - Retry logic for failed deliveries
    - Event filtering
    """

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize webhook service.

        Args:
            timeout: HTTP request timeout in seconds
            max_retries: Number of times to retry failed deliveries
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.http_client = httpx.AsyncClient(timeout=timeout)

    async def deliver_webhook(
        self,
        webhook_url: str,
        payload: WebhookPayload,
        secret: Optional[str] = None
    ) -> bool:
        """
        Deliver webhook payload to registered endpoint.

        Args:
            webhook_url: The endpoint to deliver to
            payload: The webhook payload
            secret: Optional secret for signing payload

        Returns:
            True if delivery successful, False otherwise

        Note:
            This is an async function intended to be run in background.
            Should be called with asyncio.create_task() or similar.
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "LaNature-Webhook/1.0"
        }

        # Add signature if secret provided
        if secret:
            signature = payload.sign(secret)
            headers["X-Lanature-Signature"] = signature
            headers["X-Lanature-Signature-Algorithm"] = "sha256"

        # Add event type header
        headers["X-Lanature-Event"] = payload.event.value

        payload_json = payload.to_dict()

        for attempt in range(self.max_retries):
            try:
                response = await self.http_client.post(
                    webhook_url,
                    json=payload_json,
                    headers=headers
                )

                if 200 <= response.status_code < 300:
                    logger.info(
                        f"Webhook delivered successfully to {webhook_url} "
                        f"(event: {payload.event.value}, id: {payload.event_id})"
                    )
                    return True

                elif response.status_code >= 400:
                    # Don't retry on client errors (4xx)
                    logger.warning(
                        f"Webhook rejected by {webhook_url}: "
                        f"{response.status_code} {response.reason_phrase}"
                    )
                    return False

            except httpx.TimeoutException:
                logger.warning(
                    f"Webhook delivery timeout to {webhook_url} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
            except Exception as e:
                logger.error(
                    f"Webhook delivery error to {webhook_url}: {str(e)} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)

        logger.error(
            f"Webhook delivery failed after {self.max_retries} attempts to {webhook_url}"
        )
        return False

    async def close(self):
        """Close HTTP client connection."""
        await self.http_client.aclose()


class WebhookManager:
    """
    In-memory webhook registry and management.

    Production deployments should use a database for persistence.
    """

    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[str, Dict] = {}  # webhook_id -> webhook_config
        self.user_webhooks: Dict[int, List[str]] = {}  # user_id -> webhook_ids

    def register_webhook(
        self,
        user_id: int,
        webhook_url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
        active: bool = True
    ) -> str:
        """
        Register a new webhook.

        Args:
            user_id: User registering the webhook
            webhook_url: Endpoint URL to receive webhooks
            events: List of events to subscribe to
            secret: Optional secret for HMAC signing
            active: Whether webhook is initially active

        Returns:
            Webhook ID
        """
        webhook_id = str(uuid.uuid4())

        webhook_config = {
            "id": webhook_id,
            "user_id": user_id,
            "url": webhook_url,
            "events": [e.value for e in events],
            "secret": secret,
            "active": active,
            "created_at": datetime.utcnow().isoformat(),
            "last_delivery": None,
            "delivery_count": 0,
            "failure_count": 0
        }

        self.webhooks[webhook_id] = webhook_config

        if user_id not in self.user_webhooks:
            self.user_webhooks[user_id] = []

        self.user_webhooks[user_id].append(webhook_id)

        logger.info(
            f"Webhook registered: {webhook_id} for user {user_id} "
            f"(events: {','.join([e.value for e in events])})"
        )

        return webhook_id

    def unregister_webhook(self, webhook_id: str, user_id: int) -> bool:
        """
        Unregister a webhook.

        Args:
            webhook_id: The webhook to remove
            user_id: User removing the webhook

        Returns:
            True if successful, False if webhook not found
        """
        if webhook_id not in self.webhooks:
            return False

        webhook = self.webhooks[webhook_id]
        if webhook["user_id"] != user_id:
            logger.warning(
                f"Unauthorized webhook removal attempt: {webhook_id} by user {user_id}"
            )
            return False

        del self.webhooks[webhook_id]
        self.user_webhooks[user_id].remove(webhook_id)

        logger.info(f"Webhook unregistered: {webhook_id}")
        return True

    def get_user_webhooks(self, user_id: int) -> List[Dict]:
        """Get all webhooks for a user."""
        webhook_ids = self.user_webhooks.get(user_id, [])
        return [self.webhooks[wid] for wid in webhook_ids if wid in self.webhooks]

    def get_webhooks_for_event(
        self,
        event: WebhookEvent,
        user_id: int
    ) -> List[Dict]:
        """Get webhooks for a specific event and user."""
        user_webhooks = self.get_user_webhooks(user_id)
        return [
            w for w in user_webhooks
            if w["active"] and event.value in w["events"]
        ]

    def update_webhook_delivery_status(
        self,
        webhook_id: str,
        success: bool
    ) -> None:
        """Update webhook delivery statistics."""
        if webhook_id not in self.webhooks:
            return

        webhook = self.webhooks[webhook_id]
        webhook["last_delivery"] = datetime.utcnow().isoformat()

        if success:
            webhook["delivery_count"] += 1
        else:
            webhook["failure_count"] += 1

    def toggle_webhook(self, webhook_id: str, active: bool) -> bool:
        """Enable or disable a webhook."""
        if webhook_id not in self.webhooks:
            return False

        self.webhooks[webhook_id]["active"] = active
        logger.info(f"Webhook {'enabled' if active else 'disabled'}: {webhook_id}")
        return True

    def export_webhook_config(self, webhook_id: str) -> Optional[Dict]:
        """Export webhook configuration (for display/debugging)."""
        if webhook_id not in self.webhooks:
            return None

        config = self.webhooks[webhook_id].copy()
        # Don't expose secret in export
        config["secret"] = "***" if config.get("secret") else None
        return config


# Global webhook service and manager instances
webhook_service = WebhookService()
webhook_manager = WebhookManager()
