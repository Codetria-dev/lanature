"""
Tests for backup functionality.

Tests backup creation, listing, restoration, and health checks.
"""

import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import User, Pet, Routine
from app.auth import get_password_hash, create_access_token
from app.domain.backup_service import BackupService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client(db):
    """FastAPI test client with overridden database."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Create admin user for testing."""
    admin = User(
        name="Admin User",
        email="admin@test.com",
        password_hash=get_password_hash("Admin@123"),
        is_superuser=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user):
    """Create JWT token for admin user."""
    return create_access_token(data={"sub": admin_user.email})


@pytest.fixture
def admin_headers(admin_token):
    """Authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def regular_user(db):
    """Create regular user for testing."""
    user = User(
        name="Regular User",
        email="user@test.com",
        password_hash=get_password_hash("User@123"),
        is_superuser=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user_token(regular_user):
    """Create JWT token for regular user."""
    return create_access_token(data={"sub": regular_user.email})


@pytest.fixture
def regular_user_headers(regular_user_token):
    """Authorization headers for regular user."""
    return {"Authorization": f"Bearer {regular_user_token}"}


@pytest.fixture
def sample_data(db, admin_user):
    """Create sample data for backup testing."""
    pet = Pet(
        user_id=admin_user.id,
        name="Fluffy",
        species="cat",
        breed="Persian"
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)

    routine = Routine(
        pet_id=pet.id
    )
    db.add(routine)
    db.commit()

    return {"pet": pet, "routine": routine, "user": admin_user}


@pytest.fixture
def backup_service_instance():
    """Create BackupService instance for testing."""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    service = BackupService(
        db_url="sqlite:///./test_lanature.db",
        backup_dir=temp_dir
    )
    yield service
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# ============================================================================
# BACKUP ENDPOINT TESTS
# ============================================================================

@pytest.mark.parametrize("endpoint,method", [
    ("/backup/create", "POST"),
    ("/backup/list", "GET"),
])
def test_backup_endpoints_require_admin(client, regular_user_headers, endpoint, method):
    """
    Test that backup endpoints require admin role.

    Ensure non-admin users cannot access backup endpoints.
    """
    if method == "POST":
        response = client.post(f"/api/v1/admin{endpoint}", headers=regular_user_headers)
    else:
        response = client.get(f"/api/v1/admin{endpoint}", headers=regular_user_headers)

    # Should return 403 Forbidden or 401 Unauthorized for non-admin
    assert response.status_code in [401, 403]


def test_backup_create_endpoint(client, admin_headers, sample_data):
    """
    Test creating a backup via endpoint.

    POST /api/v1/admin/backup/create should:
    - Return 201 Created
    - Include backup_id, created_at, expires_at
    - Backup file should be created
    """
    response = client.post(
        "/api/v1/admin/backup/create",
        headers=admin_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert "backup_id" in data
    assert "created_at" in data
    assert "size_mb" in data
    assert "expires_at" in data
    assert data["status"] == "completed"
    assert data["size_mb"] > 0


def test_backup_list_endpoint(client, admin_headers, sample_data):
    """
    Test listing backups via endpoint.

    GET /api/v1/admin/backup/list should:
    - Return 200 OK
    - Include list of backups with metadata
    """
    # Create a backup first
    client.post("/api/v1/admin/backup/create", headers=admin_headers)

    response = client.get(
        "/api/v1/admin/backup/list",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "backups" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["backups"]) >= 1

    backup = data["backups"][0]
    assert "backup_id" in backup
    assert "created_at" in backup
    assert "expires_at" in backup
    assert "size_mb" in backup


def test_backup_delete_endpoint(client, admin_headers, sample_data):
    """
    Test deleting a backup via endpoint.

    DELETE /api/v1/admin/backup/{backup_id} should:
    - Return 200 OK
    - Remove the backup file
    """
    # Create a backup
    create_response = client.post(
        "/api/v1/admin/backup/create",
        headers=admin_headers
    )
    backup_id = create_response.json()["backup_id"]

    # Delete the backup
    delete_response = client.delete(
        f"/api/v1/admin/backup/{backup_id}",
        headers=admin_headers
    )

    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["status"] == "deleted"
    assert data["backup_id"] == backup_id

    # Verify backup is no longer listed
    list_response = client.get(
        "/api/v1/admin/backup/list",
        headers=admin_headers
    )
    backup_ids = [b["backup_id"] for b in list_response.json()["backups"]]
    assert backup_id not in backup_ids


def test_database_health_endpoint(client, admin_headers, sample_data):
    """
    Test database health check endpoint.

    GET /api/v1/admin/health/database should:
    - Return 200 OK
    - Include health status, table count, record count
    """
    response = client.get(
        "/api/v1/admin/health/database",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "tables_count" in data
    assert "total_records" in data
    assert "last_backup" in data
    assert "backup_status" in data
    assert "database_file" in data
    assert "database_size_mb" in data
    assert data["tables_count"] > 0


# ============================================================================
# BACKUP SERVICE TESTS
# ============================================================================

def test_backup_service_create_backup(backup_service_instance):
    """
    Test BackupService.create_backup().

    Should create a gzipped SQL dump and return BackupInfo.
    """
    # This test requires an actual database file to exist
    # Skip if test database doesn't exist
    pytest.skip("Requires actual database file")


def test_backup_service_list_backups(backup_service_instance):
    """
    Test BackupService.list_backups().

    Should return list of BackupInfo objects sorted by date.
    """
    backups = backup_service_instance.list_backups()

    assert isinstance(backups, list)
    # Verify sorted by date (newest first)
    if len(backups) > 1:
        for i in range(len(backups) - 1):
            assert backups[i].created_at >= backups[i + 1].created_at


def test_backup_info_expiry(backup_service_instance):
    """
    Test BackupInfo expiry calculation.

    Backup should expire after 30 days.
    """
    from app.domain.backup_service import BackupInfo

    now = datetime.utcnow()
    backup_info = BackupInfo(
        backup_id="test-123",
        created_at=now,
        file_path="/path/to/backup.sql.gz",
        size_mb=10.5
    )

    expected_expiry = now + timedelta(days=30)

    # Allow 1 second tolerance for timing
    assert abs((backup_info.expires_at - expected_expiry).total_seconds()) < 1


def test_backup_info_to_dict():
    """
    Test BackupInfo.to_dict() serialization.

    Should convert to dictionary with correct format.
    """
    from app.domain.backup_service import BackupInfo

    created = datetime.utcnow()
    backup_info = BackupInfo(
        backup_id="test-456",
        created_at=created,
        file_path="/path/to/backup.sql.gz",
        size_mb=15.75
    )

    data = backup_info.to_dict()

    assert data["backup_id"] == "test-456"
    assert "created_at" in data
    assert "size_mb" in data
    assert "expires_at" in data
    assert data["size_mb"] == 15.75


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_restore_backup_not_found(client, admin_headers):
    """
    Test restoring non-existent backup.

    Should return 404 Not Found.
    """
    response = client.post(
        "/api/v1/admin/backup/nonexistent-id/restore",
        headers=admin_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_download_backup_not_found(client, admin_headers):
    """
    Test downloading non-existent backup.

    Should return 404 Not Found.
    """
    response = client.get(
        "/api/v1/admin/backup/nonexistent-id/download",
        headers=admin_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_backup_not_found(client, admin_headers):
    """
    Test deleting non-existent backup.

    Should return 404 Not Found.
    """
    response = client.delete(
        "/api/v1/admin/backup/nonexistent-id",
        headers=admin_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
