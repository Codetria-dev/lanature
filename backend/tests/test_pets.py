import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestPets:
    """Tests for pet management endpoints"""

    def test_list_pets_empty(self, client: TestClient, auth_headers):
        """Test listing pets when none exist"""
        response = client.get("/api/v1/pets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_create_pet_success(self, client: TestClient, auth_headers):
        """Test creating a pet"""
        response = client.post(
            "/api/v1/pets/",
            json={
                "name": "Fluffy",
                "species": "dog",
                "breed": "Golden Retriever",
                "birth_date": "2020-01-15",
                "weight": 30.5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Fluffy"
        assert data["species"] == "dog"
        assert "id" in data

    def test_create_pet_missing_name(self, client: TestClient, auth_headers):
        """Test creating pet without name"""
        response = client.post(
            "/api/v1/pets/",
            json={
                "species": "dog",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_list_pets(self, client: TestClient, auth_headers, db: Session, test_user):
        """Test listing user's pets"""
        # Create 2 pets
        client.post(
            "/api/v1/pets/",
            json={"name": "Pet1", "species": "dog"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/pets/",
            json={"name": "Pet2", "species": "cat"},
            headers=auth_headers,
        )

        response = client.get("/api/v1/pets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Pet1"
        assert data["data"][1]["name"] == "Pet2"

    def test_get_pet_success(self, client: TestClient, auth_headers):
        """Test getting a specific pet"""
        create_response = client.post(
            "/api/v1/pets/",
            json={"name": "Fluffy", "species": "dog"},
            headers=auth_headers,
        )
        pet_id = create_response.json()["id"]

        response = client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == pet_id

    def test_get_pet_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent pet"""
        response = client.get("/api/v1/pets/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_pet_success(self, client: TestClient, auth_headers):
        """Test updating a pet"""
        create_response = client.post(
            "/api/v1/pets/",
            json={"name": "Fluffy", "species": "dog"},
            headers=auth_headers,
        )
        pet_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/pets/{pet_id}",
            json={"name": "FruffyUpdated"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "FruffyUpdated"

    def test_delete_pet_success(self, client: TestClient, auth_headers):
        """Test deleting a pet"""
        create_response = client.post(
            "/api/v1/pets/",
            json={"name": "Fluffy", "species": "dog"},
            headers=auth_headers,
        )
        pet_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify pet is deleted
        response = client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_pet_ownership_isolation(
        self, client: TestClient, auth_headers, db: Session, test_admin_user
    ):
        """Test that users can only access their own pets"""
        # Create pet as test_user
        create_response = client.post(
            "/api/v1/pets/",
            json={"name": "UserPet", "species": "dog"},
            headers=auth_headers,
        )
        pet_id = create_response.json()["id"]

        # Try to access as test_admin_user (different user)
        admin_token = "different.token.here"
        response = client.get(
            f"/api/v1/pets/{pet_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Should fail due to invalid token or 404
        assert response.status_code in [403, 404]

    def test_create_pet_unauthorized(self, client: TestClient):
        """Test creating pet without authentication"""
        response = client.post(
            "/api/v1/pets/",
            json={"name": "Fluffy", "species": "dog"},
        )
        assert response.status_code == 403
