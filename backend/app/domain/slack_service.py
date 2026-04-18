"""
Slack notification service.

Sends reminders and notifications to Slack via incoming webhooks.
No OAuth required - uses pre-configured webhook URLs.
"""

import httpx
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackService:
    """
    Slack integration service using incoming webhooks.

    Features:
    - Send task reminders to Slack
    - Send daily summaries
    - Send critical alerts
    - No OAuth required (webhook-based)
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize Slack service.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout

    @staticmethod
    def send_slack_message(webhook_url: str, message: dict) -> bool:
        """
        Send message to Slack via webhook.

        Args:
            webhook_url: Slack incoming webhook URL
            message: Message payload (Block Kit format)

        Returns:
            True if message sent successfully

        Note:
            This is a synchronous method. For better performance,
            call in background task (FastAPI background_tasks).
        """
        if not webhook_url:
            logger.warning("No Slack webhook URL configured")
            return False

        try:
            response = httpx.post(webhook_url, json=message, timeout=10)

            if response.status_code == 200:
                logger.info("Slack message sent successfully")
                return True
            else:
                logger.error(f"Slack webhook returned {response.status_code}: {response.text}")
                return False

        except httpx.TimeoutException:
            logger.error("Slack webhook request timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False

    @staticmethod
    def format_task_reminder(
        pet_name: str,
        task_type: str,
        task_time: str,
        user_name: str
    ) -> dict:
        """
        Format task reminder message for Slack.

        Args:
            pet_name: Name of the pet
            task_type: Type of task (feeding, medication, etc.)
            task_time: Time the task is scheduled
            user_name: Name of the user

        Returns:
            Slack message payload in Block Kit format
        """
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🐾 Pet Care Reminder"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Pet:*\n{pet_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Task:*\n{task_type.title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Scheduled Time:*\n{task_time}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*User:*\n{user_name}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Don't forget your pet care routine! 💙"
                    }
                }
            ]
        }

    @staticmethod
    def format_daily_summary(
        user_name: str,
        completed_tasks: int,
        pending_tasks: int,
        completion_rate: float
    ) -> dict:
        """
        Format daily summary message for Slack.

        Args:
            user_name: Name of the user
            completed_tasks: Number of completed tasks
            pending_tasks: Number of pending tasks
            completion_rate: Completion rate percentage

        Returns:
            Slack message payload in Block Kit format
        """
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Daily Pet Care Summary"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*User:*\n{user_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:*\n{datetime.utcnow().strftime('%Y-%m-%d')}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"✅ *Completed:*\n{completed_tasks} tasks"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏳ *Pending:*\n{pending_tasks} tasks"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"📈 *Completion Rate:*\n{completion_rate:.1f}%"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Great job taking care of your pets! 🎉"
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def format_alert(alert_type: str, message: str) -> dict:
        """
        Format alert message for Slack.

        Args:
            alert_type: Type of alert (warning, error, info)
            message: Alert message

        Returns:
            Slack message payload in Block Kit format
        """
        color_map = {
            "warning": "warning",
            "error": "danger",
            "info": "good",
            "success": "good"
        }

        color = color_map.get(alert_type, "warning")
        emoji_map = {
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "success": "✅"
        }
        emoji = emoji_map.get(alert_type, "ℹ️")

        return {
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} {alert_type.title()} Alert",
                    "text": message,
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }


class SlackWebhookConfig:
    """Configuration for Slack webhook integration."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack webhook configuration.

        Args:
            webhook_url: Slack incoming webhook URL
        """
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)

    def is_configured(self) -> bool:
        """Check if Slack webhook is properly configured."""
        return self.enabled and bool(self.webhook_url)


# Global Slack service instance
slack_service = SlackService()
