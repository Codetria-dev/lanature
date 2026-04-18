import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.admin
class TestAdmin:
    """Tests for admin endpoints"""

    def test_list_users_success(
        self, client: TestClient, admin_headers, test_user
    ):
        """Test admin listing all users"""
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_users_unauthorized(
        self, client: TestClient, auth_headers, test_user
    ):
        """Test regular user cannot access admin endpoints"""
        response = client.get("/api/v1/admin/users", headers=auth_headers)
        assert response.status_code == 403

    def test_list_users_no_auth(self, client: TestClient):
        """Test accessing admin without authentication"""
        response = client.get("/api/v1/admin/users")
        assert response.status_code == 403

    def test_deactivate_user_success(
        self, client: TestClient, admin_headers, test_user
    ):
        """Test admin deactivating a user"""
        response = client.patch(
            f"/api/v1/admin/users/{test_user.id}/deactivate",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_activate_user_success(
        self, client: TestClient, admin_headers, test_user, db: Session
    ):
        """Test admin activating a user"""
        test_user.is_active = False
        db.commit()

        response = client.patch(
            f"/api/v1/admin/users/{test_user.id}/activate",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is True

    def test_delete_user_success(
        self, client: TestClient, admin_headers, test_user
    ):
        """Test admin deleting a user"""
        user_id = test_user.id

        response = client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=admin_headers,
        )
        assert response.status_code == 204

        # Verify user is deleted
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
        )
        users = response.json()
        user_ids = [u["id"] for u in users]
        assert user_id not in user_ids

    def test_get_stats_success(self, client: TestClient, admin_headers):
        """Test admin getting system statistics"""
        response = client.get(
            "/api/v1/admin/stats",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_pets" in data
        assert "total_routines" in data

    def test_get_settings_success(self, client: TestClient, admin_headers):
        """Test admin getting settings"""
        response = client.get(
            "/api/v1/admin/settings",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_setting_success(
        self, client: TestClient, admin_headers
    ):
        """Test admin updating a setting"""
        response = client.patch(
            "/api/v1/admin/settings/registration_enabled",
            json={"value": "false"},
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_update_setting_invalid_value(
        self, client: TestClient, admin_headers
    ):
        """Test updating setting with invalid value"""
        response = client.patch(
            "/api/v1/admin/settings/max_pets_per_user",
            json={"value": "-5"},  # Invalid negative value
            headers=admin_headers,
        )
        # May be 400 or 422 depending on validation
        assert response.status_code in [400, 422]

    def test_admin_cannot_access_user_endpoints(
        self, client: TestClient, admin_headers
    ):
        """Test admin user can still access regular user endpoints"""
        # This tests that admin_headers work for user endpoints too
        response = client.get(
            "/api/v1/auth/me",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_superuser"] is True

    def test_delete_nonexistent_user(
        self, client: TestClient, admin_headers
    ):
        """Test deleting non-existent user"""
        response = client.delete(
            "/api/v1/admin/users/99999",
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_deactivate_nonexistent_user(
        self, client: TestClient, admin_headers
    ):
        """Test deactivating non-existent user"""
        response = client.patch(
            "/api/v1/admin/users/99999/deactivate",
            headers=admin_headers,
        )
        assert response.status_code == 404
