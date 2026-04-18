"""
Tests for pagination - Phase 5 Performance Optimization

Tests pagination functionality for list endpoints:
- Pets list
- Routines list
- Logs list
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.pagination import paginate, PaginationParams
from app.models import Pet


@pytest.mark.pagination
class TestPaginationHelper:
    """Tests for pagination utility functions"""

    def test_pagination_params_defaults(self):
        """Test PaginationParams default values"""
        params = PaginationParams()
        assert params.page == 1
        assert params.limit == 10

    def test_pagination_params_validation(self):
        """Test PaginationParams validation"""
        # Valid
        params = PaginationParams(page=2, limit=50)
        assert params.page == 2
        assert params.limit == 50

        # Invalid page (should fail)
        with pytest.raises(ValueError):
            PaginationParams(page=0)

    def test_paginate_first_page(self, db: Session, test_user):
        """Test pagination on first page"""
        # Create 25 pets
        for i in range(25):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Paginate with limit 10
        query = db.query(Pet).filter(Pet.user_id == test_user.id)
        result = paginate(query, page=1, limit=10)

        assert len(result["data"]) == 10
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 10
        assert result["pagination"]["total"] == 25
        assert result["pagination"]["pages"] == 3
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_previous"] is False

    def test_paginate_middle_page(self, db: Session, test_user):
        """Test pagination on middle page"""
        # Create 25 pets
        for i in range(25):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Paginate page 2
        query = db.query(Pet).filter(Pet.user_id == test_user.id)
        result = paginate(query, page=2, limit=10)

        assert len(result["data"]) == 10
        assert result["pagination"]["page"] == 2
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_previous"] is True

    def test_paginate_last_page(self, db: Session, test_user):
        """Test pagination on last page"""
        # Create 25 pets
        for i in range(25):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Paginate page 3 (last page)
        query = db.query(Pet).filter(Pet.user_id == test_user.id)
        result = paginate(query, page=3, limit=10)

        assert len(result["data"]) == 5  # Remaining items
        assert result["pagination"]["page"] == 3
        assert result["pagination"]["has_next"] is False
        assert result["pagination"]["has_previous"] is True

    def test_paginate_invalid_page(self, db: Session, test_user):
        """Test pagination with invalid page number"""
        for i in range(5):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Page 999 (beyond available)
        query = db.query(Pet).filter(Pet.user_id == test_user.id)
        result = paginate(query, page=999, limit=10)

        assert result["data"] == []
        assert result["pagination"]["page"] == 999


@pytest.mark.pagination
class TestPaginationEndpoints:
    """Tests for pagination in API endpoints"""

    def test_pets_endpoint_pagination_first_page(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test pets endpoint pagination on first page"""
        # Create 5 pets
        from app.models import Pet
        for i in range(5):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Request first page
        response = client.get(
            "/api/v1/pets/?page=1&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["has_next"] is True

    def test_pets_endpoint_pagination_second_page(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test pets endpoint pagination on second page"""
        # Create 5 pets
        from app.models import Pet
        for i in range(5):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Request second page
        response = client.get(
            "/api/v1/pets/?page=2&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_previous"] is True

    def test_pets_endpoint_pagination_default(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test pets endpoint pagination with default parameters"""
        # Create 15 pets (more than default 10)
        from app.models import Pet
        for i in range(15):
            pet = Pet(
                user_id=test_user.id,
                name=f"Pet {i}",
                species="dog"
            )
            db.add(pet)
        db.commit()

        # Request with default pagination
        response = client.get(
            "/api/v1/pets/",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 10  # Default limit
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["has_next"] is True

    def test_logs_endpoint_pagination(self, client: TestClient, test_user, test_user_with_pet, auth_headers, db: Session):
        """Test logs endpoint pagination"""
        # Create routine logs
        from app.models import RoutineLog

        pet = test_user_with_pet
        routine = pet.routine
        task = routine.tasks[0] if routine.tasks else None

        if not task:
            from app.models import RoutineTask
            task = RoutineTask(
                routine_id=routine.id,
                type="feeding",
                frequency="daily",
                time="09:00"
            )
            db.add(task)
            db.commit()

        # Create 25 logs
        from datetime import datetime, timedelta
        for i in range(25):
            log = RoutineLog(
                task_id=task.id,
                date=(datetime.now() - timedelta(days=i)).date(),
                status="DONE"
            )
            db.add(log)
        db.commit()

        # Request paginated logs
        response = client.get(
            "/api/v1/logs/?page=1&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["pages"] == 3

    def test_pagination_limit_cap(self, client: TestClient, test_user, auth_headers):
        """Test that pagination limit is capped at 100"""
        # Request with limit > 100
        response = client.get(
            "/api/v1/pets/?page=1&limit=500",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["pagination"]["limit"] <= 100  # Should be capped

    def test_pagination_page_zero_defaults(self, client: TestClient, test_user, auth_headers):
        """Test that page 0 defaults to page 1"""
        response = client.get(
            "/api/v1/pets/?page=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # Page should be at least 1
        assert data["pagination"]["page"] >= 1
