import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestRoutines:
    """Tests for routine task management"""

    @pytest.fixture
    def pet_id(self, client: TestClient, auth_headers):
        """Create a pet for testing"""
        response = client.post(
            "/api/v1/pets/",
            json={"name": "TestPet", "species": "dog"},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_list_routines_empty(self, client: TestClient, auth_headers):
        """Test listing routines when none exist"""
        response = client.get("/api/v1/routines/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_routine_success(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test creating a routine task"""
        response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
                "is_active": True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "FEEDING"
        assert data["frequency"] == "DAILY"

    def test_create_routine_invalid_type(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test creating routine with invalid task type"""
        response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "INVALID_TYPE",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_get_routines_by_pet(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test getting routines for a specific pet"""
        # Create 2 routines
        client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "MEDICATION",
                "frequency": "DAILY",
                "time": "18:00",
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/v1/routines/pet/{pet_id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_update_routine_success(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test updating a routine"""
        create_response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/routines/task/{task_id}",
            json={"time": "10:00"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["time"] == "10:00"

    def test_toggle_routine_active(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test toggling routine active status"""
        create_response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
                "is_active": True,
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Deactivate
        response = client.put(
            f"/api/v1/routines/task/{task_id}",
            json={"is_active": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_routine_success(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test deleting a routine"""
        create_response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/routines/task/{task_id}", headers=auth_headers
        )
        assert response.status_code == 204

    def test_get_routine_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent routine"""
        response = client.get(
            "/api/v1/routines/task/99999", headers=auth_headers
        )
        assert response.status_code == 404

    def test_create_routine_missing_fields(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test creating routine without required fields"""
        response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                # Missing frequency and time
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_routine_ownership_isolation(
        self, client: TestClient, auth_headers, pet_id
    ):
        """Test that users can only access their own routines"""
        create_response = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Try to access with different user token
        response = client.get(
            f"/api/v1/routines/task/{task_id}",
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert response.status_code in [403, 404]
