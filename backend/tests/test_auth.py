import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.auth
class TestAuth:
    """Tests for authentication endpoints"""

    def test_register_success(self, client: TestClient):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Another User",
                "email": "test@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "User",
                "email": "invalid-email",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422

    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # Missing name and password
            },
        )
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password",
            },
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, client: TestClient, db: Session, test_user):
        """Test login with inactive user"""
        test_user.is_active = False
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()

    def test_get_current_user_success(self, client: TestClient, auth_headers):
        """Test getting current user profile"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 403

    def test_update_user_success(self, client: TestClient, auth_headers):
        """Test updating user profile"""
        response = client.put(
            "/api/v1/auth/me",
            json={
                "name": "Updated User",
                "email": "updated@example.com",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated User"
        assert data["email"] == "updated@example.com"

    def test_update_user_unauthorized(self, client: TestClient):
        """Test updating user without authentication"""
        response = client.put(
            "/api/v1/auth/me",
            json={
                "name": "Updated User",
            },
        )
        assert response.status_code == 403

    def test_update_user_duplicate_email(
        self, client: TestClient, auth_headers, db: Session, test_admin_user
    ):
        """Test updating user with existing email"""
        response = client.put(
            "/api/v1/auth/me",
            json={
                "email": test_admin_user.email,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
