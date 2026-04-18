"""
Tests for analytics endpoints - Phase 4 Data & Analytics

Tests analytics functionality for:
- User overview metrics
- Pet-specific analytics
- Historical trends
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from app.models import Pet, RoutineTask, RoutineLog
from app.constants import RoutineLogStatus


@pytest.mark.analytics
class TestAnalyticsOverview:
    """Tests for analytics overview endpoint"""

    def test_analytics_overview_no_data(self, client: TestClient, test_user, auth_headers):
        """Test overview with no tasks completed"""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "total_pets" in data
        assert "tasks_completed_today" in data
        assert "completion_rate" in data

    def test_analytics_overview_with_data(
        self,
        client: TestClient,
        test_user,
        test_user_with_pet,
        auth_headers,
        db: Session
    ):
        """Test overview with completed tasks"""
        pet = test_user_with_pet
        routine = pet.routine

        if not routine.tasks:
            task = RoutineTask(
                routine_id=routine.id,
                type="feeding",
                frequency="daily",
                time="09:00"
            )
            db.add(task)
            db.commit()
        else:
            task = routine.tasks[0]

        # Create a log for today
        log = RoutineLog(
            task_id=task.id,
            date=date.today(),
            status=RoutineLogStatus.DONE.value
        )
        db.add(log)
        db.commit()

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["tasks_completed_today"] > 0
        assert data["completion_rate"] > 0
        assert "most_active_pet" in data

    def test_analytics_overview_fields(self, client: TestClient, test_user, auth_headers):
        """Test that overview returns all required fields"""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "total_pets",
            "total_routines",
            "tasks_completed_today",
            "tasks_pending",
            "completion_rate",
            "streak_days",
            "most_active_pet",
            "this_week",
        ]

        for field in required_fields:
            assert field in data

        assert isinstance(data["this_week"], dict)
        assert "tasks_completed" in data["this_week"]
        assert "tasks_scheduled" in data["this_week"]


@pytest.mark.analytics
class TestAnalyticsPet:
    """Tests for pet-specific analytics endpoint"""

    def test_analytics_pet_not_found(self, client: TestClient, test_user, auth_headers):
        """Test analytics for non-existent pet"""
        response = client.get("/api/v1/analytics/pet/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_analytics_pet_no_tasks(
        self,
        client: TestClient,
        test_user,
        test_user_with_pet,
        auth_headers
    ):
        """Test analytics for pet with no tasks"""
        pet = test_user_with_pet
        response = client.get(f"/api/v1/analytics/pet/{pet.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["pet_name"] == pet.name
        assert data["total_tasks"] == 0
        assert data["completion_rate"] == 0

    def test_analytics_pet_with_tasks(
        self,
        client: TestClient,
        test_user,
        test_user_with_pet,
        auth_headers,
        db: Session
    ):
        """Test analytics for pet with completed tasks"""
        pet = test_user_with_pet
        routine = pet.routine

        if not routine.tasks:
            task = RoutineTask(
                routine_id=routine.id,
                type="feeding",
                frequency="daily",
                time="09:00"
            )
            db.add(task)
            db.commit()
        else:
            task = routine.tasks[0]

        # Add logs
        for i in range(5):
            status = RoutineLogStatus.DONE.value if i < 3 else RoutineLogStatus.SKIPPED.value
            log = RoutineLog(
                task_id=task.id,
                date=(date.today() - timedelta(days=i)),
                status=status
            )
            db.add(log)
        db.commit()

        response = client.get(f"/api/v1/analytics/pet/{pet.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_tasks"] >= 5
        assert data["completed"] == 3
        assert data["completion_rate"] > 0

    def test_analytics_pet_unauthorized_access(
        self,
        client: TestClient,
        test_user,
        other_user,
        test_user_with_pet,
        auth_headers
    ):
        """Test that users can't view other users' pet analytics"""
        pet = test_user_with_pet

        other_headers = {
            "Authorization": f"Bearer {other_user['token']}"
        }

        response = client.get(f"/api/v1/analytics/pet/{pet.id}", headers=other_headers)
        assert response.status_code == 404


@pytest.mark.analytics
class TestAnalyticsHistory:
    """Tests for historical analytics endpoint"""

    def test_analytics_history_default_days(self, client: TestClient, test_user, auth_headers):
        """Test history with default 30 days"""
        response = client.get("/api/v1/analytics/history", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "daily_data" in data
        assert "trend" in data
        assert "avg_completion_rate" in data
        assert len(data["daily_data"]) == 30

    def test_analytics_history_custom_days(self, client: TestClient, test_user, auth_headers):
        """Test history with custom day range"""
        response = client.get("/api/v1/analytics/history?days=7", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["daily_data"]) == 7

    def test_analytics_history_invalid_days(self, client: TestClient, test_user, auth_headers):
        """Test history with invalid day range"""
        # Too many days
        response = client.get("/api/v1/analytics/history?days=400", headers=auth_headers)
        assert response.status_code == 400

        # Too few days
        response = client.get("/api/v1/analytics/history?days=0", headers=auth_headers)
        assert response.status_code == 400

    def test_analytics_history_daily_data_structure(
        self,
        client: TestClient,
        test_user,
        auth_headers,
        db: Session
    ):
        """Test that daily data has correct structure"""
        response = client.get("/api/v1/analytics/history?days=7", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for daily in data["daily_data"]:
            assert "date" in daily
            assert "completed" in daily
            assert "scheduled" in daily
            assert isinstance(daily["completed"], int)
            assert isinstance(daily["scheduled"], int)

    def test_analytics_history_trend(
        self,
        client: TestClient,
        test_user,
        test_user_with_pet,
        auth_headers,
        db: Session
    ):
        """Test that trend is calculated correctly"""
        # Add lots of completed tasks for recent dates
        pet = test_user_with_pet
        routine = pet.routine

        if not routine.tasks:
            task = RoutineTask(
                routine_id=routine.id,
                type="feeding",
                frequency="daily",
                time="09:00"
            )
            db.add(task)
            db.commit()
        else:
            task = routine.tasks[0]

        # Add recent tasks
        for i in range(7):
            log = RoutineLog(
                task_id=task.id,
                date=(date.today() - timedelta(days=i)),
                status=RoutineLogStatus.DONE.value
            )
            db.add(log)
        db.commit()

        response = client.get("/api/v1/analytics/history?days=30", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["trend"] in ["up", "down", "stable"]
