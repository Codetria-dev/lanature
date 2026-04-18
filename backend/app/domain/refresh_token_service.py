"""
Refresh token service for managing session tokens.

Implements refresh token rotation pattern:
- Access tokens: short-lived (30 minutes)
- Refresh tokens: long-lived (7 days)
- Token rotation: issuing new refresh token invalidates old one
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import RefreshToken, User


class RefreshTokenService:
    """Service for managing refresh tokens."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate a secure random token.

        Args:
            length: Token length in bytes

        Returns:
            URL-safe random token
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token for storage in database.

        Args:
            token: Plain text token

        Returns:
            SHA256 hash of token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def create_refresh_token(
        db: Session,
        user: User,
        expires_in_days: int = 7
    ) -> str:
        """
        Create a new refresh token for a user.

        Args:
            db: Database session
            user: User object
            expires_in_days: Token validity duration

        Returns:
            Plain text refresh token (return to client)
        """
        token = RefreshTokenService.generate_token()
        token_hash = RefreshTokenService.hash_token(token)

        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(db_token)
        db.commit()

        return token

    @staticmethod
    def validate_refresh_token(db: Session, user: User, token: str) -> bool:
        """
        Validate a refresh token.

        Args:
            db: Database session
            user: User object
            token: Plain text refresh token to validate

        Returns:
            True if valid, False otherwise
        """
        token_hash = RefreshTokenService.hash_token(token)

        db_token = db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user.id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).first()

        return db_token is not None

    @staticmethod
    def refresh_token_pair(
        db: Session,
        user: User,
        old_token: str
    ) -> tuple:
        """
        Exchange a refresh token for new access + refresh token pair.

        Invalidates old refresh token (token rotation).

        Args:
            db: Database session
            user: User object
            old_token: Current refresh token

        Returns:
            Tuple of (new_access_token_string, new_refresh_token_string)
            Returns (None, None) if token is invalid
        """
        # Validate old token
        if not RefreshTokenService.validate_refresh_token(db, user, old_token):
            return None, None

        # Invalidate old token
        old_token_hash = RefreshTokenService.hash_token(old_token)
        old_db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == old_token_hash
        ).first()

        if old_db_token:
            old_db_token.is_revoked = True
            old_db_token.revoked_at = datetime.utcnow()

        # Create new token
        new_refresh_token = RefreshTokenService.create_refresh_token(db, user)

        return new_refresh_token

    @staticmethod
    def revoke_user_tokens(db: Session, user: User):
        """
        Revoke all refresh tokens for a user (logout).

        Args:
            db: Database session
            user: User object
        """
        db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user.id,
                RefreshToken.is_revoked == False
            )
        ).update({
            RefreshToken.is_revoked: True,
            RefreshToken.revoked_at: datetime.utcnow()
        })
        db.commit()

    @staticmethod
    def cleanup_expired_tokens(db: Session):
        """
        Delete expired refresh tokens (cleanup task).

        Should be run periodically (e.g., daily).

        Args:
            db: Database session
        """
        db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
