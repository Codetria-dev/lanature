from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import EmailVerificationToken, PasswordResetToken, User


class SecurityTokensService:
    @staticmethod
    def _generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_password_reset_token(db: Session, user: User, expires_minutes: int = 30) -> PasswordResetToken:
        token = SecurityTokensService._generate_token()
        entry = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def consume_password_reset_token(db: Session, token: str) -> User | None:
        entry = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token == token, PasswordResetToken.used_at.is_(None))
            .first()
        )
        if not entry:
            return None
        if entry.expires_at < datetime.utcnow():
            return None
        user = db.query(User).filter(User.id == entry.user_id).first()
        if not user:
            return None
        entry.used_at = datetime.utcnow()
        db.commit()
        return user

    @staticmethod
    def create_email_verification_token(db: Session, user: User, expires_hours: int = 24) -> EmailVerificationToken:
        token = SecurityTokensService._generate_token()
        entry = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def consume_email_verification_token(db: Session, token: str) -> User | None:
        entry = (
            db.query(EmailVerificationToken)
            .filter(EmailVerificationToken.token == token, EmailVerificationToken.used_at.is_(None))
            .first()
        )
        if not entry:
            return None
        if entry.expires_at < datetime.utcnow():
            return None
        user = db.query(User).filter(User.id == entry.user_id).first()
        if not user:
            return None
        entry.used_at = datetime.utcnow()
        user.email_verified = True
        db.commit()
        db.refresh(user)
        return user


security_tokens_service = SecurityTokensService()
