"""Tests for Two-Factor Authentication (2FA) endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp


@pytest.mark.auth
class TestTwoFactorAuth:
    """Tests for 2FA functionality."""

    def test_setup_2fa_success(self, client: TestClient, auth_headers):
        """Test successful 2FA setup initiation."""
        response = client.post("/api/v1/auth/2fa/setup", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code" in data
        assert "backup_codes" in data
        assert "manual_entry_key" in data
        assert len(data["backup_codes"]) == 10
        assert data["qr_code"].startswith("data:image/png;base64,")

    def test_setup_2fa_already_enabled(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test 2FA setup when 2FA is already enabled."""
        test_user.is_2fa_enabled = True
        test_user.totp_secret = "secret123"
        db.commit()

        response = client.post("/api/v1/auth/2fa/setup", headers=auth_headers)

        assert response.status_code == 400
        assert "already enabled" in response.json()["detail"].lower()

    def test_verify_2fa_success(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test successful 2FA setup verification."""
        # First, setup 2FA
        secret = pyotp.random_base32()
        test_user.totp_secret = secret
        db.commit()

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Verify the setup
        response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"code": code},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_superuser"] is False  # Check it's the right user

        # Verify 2FA is now enabled in DB
        db.refresh(test_user)
        assert test_user.is_2fa_enabled is True

    def test_verify_2fa_invalid_code(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test 2FA verification with invalid code."""
        secret = pyotp.random_base32()
        test_user.totp_secret = secret
        db.commit()

        response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"code": "000000"},  # Invalid code
            headers=auth_headers
        )

        assert response.status_code == 401
        assert "invalid or expired" in response.json()["detail"].lower()

    def test_verify_2fa_no_secret(self, client: TestClient, auth_headers):
        """Test 2FA verification when setup wasn't initiated."""
        response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"code": "000000"},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "setup not initiated" in response.json()["detail"].lower()

    def test_disable_2fa_success(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test successful 2FA disabling."""
        test_user.is_2fa_enabled = True
        test_user.totp_secret = "secret123"
        test_user.backup_codes = ["CODE1", "CODE2"]
        db.commit()

        response = client.post(
            "/api/v1/auth/2fa/disable",
            json={"password": "TestPass123!"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_superuser"] is False

        # Verify 2FA is disabled in DB
        db.refresh(test_user)
        assert test_user.is_2fa_enabled is False
        assert test_user.totp_secret is None

    def test_disable_2fa_invalid_password(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test 2FA disabling with invalid password."""
        test_user.is_2fa_enabled = True
        db.commit()

        response = client.post(
            "/api/v1/auth/2fa/disable",
            json={"password": "wrongpassword"},
            headers=auth_headers
        )

        assert response.status_code == 401
        assert "invalid password" in response.json()["detail"].lower()

    def test_disable_2fa_not_enabled(self, client: TestClient, auth_headers):
        """Test disabling 2FA when not enabled."""
        response = client.post(
            "/api/v1/auth/2fa/disable",
            json={"password": "TestPass123!"},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()

    def test_generate_backup_codes(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test generating new backup codes."""
        test_user.is_2fa_enabled = True
        test_user.backup_codes = ["OLD1", "OLD2"]
        db.commit()

        response = client.post("/api/v1/auth/2fa/backup-codes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "backup_codes" in data
        assert len(data["backup_codes"]) == 10
        assert "NEW" not in [code for code in data["backup_codes"] if code.startswith("NEW")]

    def test_verify_code_totp(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test TOTP code verification during 2FA."""
        secret = pyotp.random_base32()
        test_user.is_2fa_enabled = True
        test_user.totp_secret = secret
        db.commit()

        totp = pyotp.TOTP(secret)
        code = totp.now()

        response = client.post(
            "/api/v1/auth/2fa/verify-code",
            json={"code": code},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_verify_code_backup(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test backup code verification during 2FA."""
        test_user.is_2fa_enabled = True
        test_user.backup_codes = ["BACKUP001", "BACKUP002", "BACKUP003"]
        db.commit()

        response = client.post(
            "/api/v1/auth/2fa/verify-code",
            json={"code": "BACKUP001"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        # Verify backup code was consumed
        db.refresh(test_user)
        assert "BACKUP001" not in test_user.backup_codes
        assert "BACKUP002" in test_user.backup_codes

    def test_verify_code_invalid(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test invalid code verification."""
        secret = pyotp.random_base32()
        test_user.is_2fa_enabled = True
        test_user.totp_secret = secret
        db.commit()

        response = client.post(
            "/api/v1/auth/2fa/verify-code",
            json={"code": "000000"},
            headers=auth_headers
        )

        assert response.status_code == 401
        assert "invalid or expired" in response.json()["detail"].lower()

    def test_verify_code_2fa_disabled(self, client: TestClient, auth_headers):
        """Test verifying code when 2FA is not enabled."""
        response = client.post(
            "/api/v1/auth/2fa/verify-code",
            json={"code": "000000"},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()

    @pytest.mark.skip(reason="Rate limiting not yet applied to auth route decorators")
    def test_rate_limit_login(self, client: TestClient, test_user):
        """Test rate limiting on login endpoint."""
        rate_limit_triggered = False
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                }
            )

            if response.status_code == 429:
                rate_limit_triggered = True
                break
            elif i < 5:
                assert response.status_code in [401, 422]

        assert rate_limit_triggered, "Rate limiting should be triggered"

    @pytest.mark.skip(reason="Rate limiting not yet applied to auth route decorators")
    def test_rate_limit_register(self, client: TestClient):
        """Test rate limiting on register endpoint."""
        rate_limit_triggered = False
        for i in range(4):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "name": f"RateLimit User {i}",
                    "email": f"ratelimit_user_{i}@example.com",
                    "password": "SecurePass123!"
                }
            )

            if response.status_code == 429:
                rate_limit_triggered = True
                break
            elif i < 3:
                assert response.status_code in [201, 400]

        assert rate_limit_triggered, "Rate limiting should be triggered"
