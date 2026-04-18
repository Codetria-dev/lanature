import logging


logger = logging.getLogger("lanature.notifications")


class NotificationService:
    @staticmethod
    def send_password_reset_email(email: str, token: str) -> None:
        # Provider integration (SES/Sendgrid/Postmark) can replace this implementation.
        logger.info("Password reset token generated", extra={"email": email, "token": token})

    @staticmethod
    def send_email_verification(email: str, token: str) -> None:
        logger.info("Email verification token generated", extra={"email": email, "token": token})


notification_service = NotificationService()
