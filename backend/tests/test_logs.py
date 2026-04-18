import pytest
from fastapi.testclient import TestClient
from datetime import date


@pytest.mark.crud
class TestLogs:
    """Tests for activity logging"""

    @pytest.fixture
    def pet_and_task(self, client: TestClient, auth_headers):
        """Create a pet and routine task"""
        pet_resp = client.post(
            "/api/v1/pets/",
            json={"name": "TestPet", "species": "dog"},
            headers=auth_headers,
        )
        pet_id = pet_resp.json()["id"]

        task_resp = client.post(
            "/api/v1/routines/",
            json={
                "pet_id": pet_id,
                "task_type": "FEEDING",
                "frequency": "DAILY",
                "time": "09:00",
            },
            headers=auth_headers,
        )
        task_id = task_resp.json()["id"]
        return pet_id, task_id

    def test_list_logs_empty(self, client: TestClient, auth_headers):
        """Test listing logs when none exist"""
        response = client.get("/api/v1/logs/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_log_success(self, client: TestClient, auth_headers, pet_and_task):
        """Test creating an activity log"""
        pet_id, task_id = pet_and_task

        response = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "DONE",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "DONE"
        assert "id" in data

    def test_create_log_invalid_status(
        self, client: TestClient, auth_headers, pet_and_task
    ):
        """Test creating log with invalid status"""
        pet_id, task_id = pet_and_task

        response = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "INVALID",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_get_logs_by_task(
        self, client: TestClient, auth_headers, pet_and_task
    ):
        """Test getting logs for a specific task"""
        pet_id, task_id = pet_and_task

        # Create 2 logs
        client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": "2024-01-15",
                "status": "DONE",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": "2024-01-16",
                "status": "SKIPPED",
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/v1/logs/task/{task_id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_logs_by_pet(self, client: TestClient, auth_headers, pet_and_task):
        """Test getting logs for a specific pet"""
        pet_id, task_id = pet_and_task

        client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "DONE",
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/v1/logs/pet/{pet_id}", headers=auth_headers
        )
        assert response.status_code == 200

    def test_update_log_success(
        self, client: TestClient, auth_headers, pet_and_task
    ):
        """Test updating a log"""
        pet_id, task_id = pet_and_task

        create_resp = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "DONE",
            },
            headers=auth_headers,
        )
        log_id = create_resp.json()["id"]

        response = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "SKIPPED",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["status"] == "SKIPPED"

    def test_delete_log_success(
        self, client: TestClient, auth_headers, pet_and_task
    ):
        """Test deleting a log"""
        pet_id, task_id = pet_and_task

        create_resp = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "DONE",
            },
            headers=auth_headers,
        )
        log_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/logs/{log_id}", headers=auth_headers)
        assert response.status_code == 204

    def test_log_unauthorized(self, client: TestClient, pet_and_task):
        """Test creating log without authentication"""
        pet_id, task_id = pet_and_task

        response = client.post(
            "/api/v1/logs/",
            json={
                "task_id": task_id,
                "date": str(date.today()),
                "status": "DONE",
            },
        )
        assert response.status_code == 403
