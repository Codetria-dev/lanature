"""
Admin router for administrative endpoints.

This router handles all admin-only operations:
- User management (activate/deactivate/delete)
- System statistics
- System settings

All endpoints require ADMIN role (is_superuser=True).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
from typing import List

from app.database import get_db
from app.models import User, Pet, Routine, RoutineTask, RoutineLog, Settings
from app.auth import get_current_user, require_admin_role
from app.schemas import AdminUserResponse, AdminStatsResponse, SettingsResponse, SettingsUpdate
from app.constants import RoutineLogStatus, ActiveStatus
from app.domain.settings_service import settings_service
from app.domain.backup_service import backup_service
from fastapi.responses import FileResponse

router = APIRouter()

def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Dependency to verify user has ADMIN role.
    
    Decision: Using dependency injection pattern ensures admin check happens
    before route handler executes. Centralized in one place for consistency.
    """
    return require_admin_role(current_user)

@router.get("/users", response_model=List[AdminUserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all users with their stats"""
    users = db.query(User).all()
    
    result = []
    for user in users:
        pets_count = db.query(func.count(Pet.id)).filter(Pet.user_id == user.id).scalar() or 0
        
        # Count active routine tasks for this user's pets
        # Decision: Using ActiveStatus.ACTIVE constant instead of hardcoded True
        routines_count = db.query(func.count(RoutineTask.id)).join(
            Routine, RoutineTask.routine_id == Routine.id
        ).join(
            Pet, Routine.pet_id == Pet.id
        ).filter(Pet.user_id == user.id, RoutineTask.active == ActiveStatus.ACTIVE.value).scalar() or 0
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
            "pets_count": pets_count,
            "routines_count": routines_count,
            "is_active": user.is_active
        })
    
    return result

@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Use ActiveStatus constant for clarity
    user.is_active = ActiveStatus.INACTIVE.value
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_active": user.is_active}

@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Activate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Use ActiveStatus constant for clarity
    user.is_active = ActiveStatus.ACTIVE.value
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_active": user.is_active}

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None

@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get system statistics"""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_pets = db.query(func.count(Pet.id)).scalar() or 0
    total_active_routines = db.query(func.count(RoutineTask.id)).filter(
        RoutineTask.active == ActiveStatus.ACTIVE.value
    ).scalar() or 0
    
    # Routines completed today
    # Decision: Using RoutineLogStatus.DONE constant instead of hardcoded string
    today = date.today()
    routines_completed_today = db.query(func.count(RoutineLog.id)).filter(
        and_(
            func.date(RoutineLog.date) == today,
            RoutineLog.status == RoutineLogStatus.DONE.value
        )
    ).scalar() or 0
    
    # Active users in last 7 days (users who have created logs)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    user_ids_with_logs = db.query(func.distinct(Pet.user_id)).join(
        Routine, Routine.pet_id == Pet.id
    ).join(
        RoutineTask, RoutineTask.routine_id == Routine.id
    ).join(
        RoutineLog, RoutineLog.task_id == RoutineTask.id
    ).filter(
        RoutineLog.date >= seven_days_ago.date()
    ).all()
    
    active_users_last_7_days = len(set([uid[0] for uid in user_ids_with_logs]))
    
    return {
        "total_users": total_users,
        "total_pets": total_pets,
        "total_routines": total_active_routines,
        "total_active_routines": total_active_routines,
        "routines_completed_today": routines_completed_today,
        "active_users_last_7_days": active_users_last_7_days
    }

@router.get("/settings", response_model=List[SettingsResponse])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all settings"""
    settings_service.ensure_defaults(db)
    return db.query(Settings).all()

@router.patch("/settings/{key}", response_model=SettingsResponse)
def update_setting(
    key: str,
    setting_update: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a setting"""
    settings_service.ensure_defaults(db)
    setting = db.query(Settings).filter(Settings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    if key == "registration_enabled":
        normalized = setting_update.value.strip().lower()
        if normalized not in {"true", "false"}:
            raise HTTPException(status_code=400, detail="registration_enabled must be 'true' or 'false'")
        setting.value = normalized
    elif key in {"max_pets_per_user", "max_routines_per_pet"}:
        try:
            parsed = int(setting_update.value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{key} must be a valid integer")
        if parsed <= 0:
            raise HTTPException(status_code=400, detail=f"{key} must be greater than 0")
        setting.value = str(parsed)
    else:
        setting.value = setting_update.value
    setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)

    return setting


# ============================================================================
# BACKUP ENDPOINTS (Phase 4 Part 2)
# ============================================================================

@router.post("/backup/create", status_code=201)
def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a manual database backup.

    Admin-only endpoint to trigger on-demand backup creation.
    Backups are stored as gzipped SQL dumps and retained for 30 days.

    Response includes backup ID and file information.
    """
    try:
        backup_info = backup_service.create_backup()
        return {
            "backup_id": backup_info.backup_id,
            "created_at": backup_info.created_at.isoformat(),
            "size_mb": backup_info.size_mb,
            "expires_at": backup_info.expires_at.isoformat(),
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup creation failed: {str(e)}"
        )


@router.get("/backup/list")
def list_backups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    List all available backups.

    Admin-only endpoint returning list of existing backups with metadata.
    Sorted by creation date (newest first).
    """
    backups = backup_service.list_backups()
    return {
        "backups": [b.to_dict() for b in backups],
        "total": len(backups)
    }


@router.post("/backup/{backup_id}/restore", status_code=200)
def restore_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Restore database from a backup.

    Admin-only endpoint to restore from a specific backup.
    Creates a safety backup before restoring.

    **Important:** This operation will overwrite the current database.
    Proceed with caution.

    Response includes restoration status and created safety backup.
    """
    try:
        # Verify backup integrity first
        if not backup_service.verify_backup_integrity(backup_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Backup is corrupted or invalid"
            )

        # Restore the backup (creates safety backup internally)
        success = backup_service.restore_backup(backup_id)

        if success:
            return {
                "status": "restored",
                "backup_id": backup_id,
                "restored_at": datetime.utcnow().isoformat(),
                "message": "Database restored successfully. A safety backup was created before restoration."
            }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup {backup_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restoration failed: {str(e)}"
        )


@router.get("/backup/{backup_id}/download")
def download_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Download a backup file.

    Admin-only endpoint to download a backup for external storage.
    Returns gzipped SQL dump file.
    """
    try:
        backup_path = backup_service.get_backup_file_path(backup_id)

        if not backup_path or not backup_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backup {backup_id} not found"
            )

        return FileResponse(
            path=backup_path,
            filename=backup_path.name,
            media_type="application/gzip"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/health/database")
def database_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Check database health status.

    Admin-only endpoint returning database health metrics:
    - Database status (healthy/unhealthy)
    - Number of tables
    - Total records across all tables
    - Last backup time
    - Database file size

    Useful for monitoring and diagnostics.
    """
    try:
        health = backup_service.get_database_health()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.delete("/backup/{backup_id}")
def delete_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a backup.

    Admin-only endpoint to manually delete a backup file.
    """
    try:
        backup_path = backup_service.get_backup_file_path(backup_id)

        if not backup_path or not backup_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backup {backup_id} not found"
            )

        backup_path.unlink()

        return {
            "status": "deleted",
            "backup_id": backup_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )
