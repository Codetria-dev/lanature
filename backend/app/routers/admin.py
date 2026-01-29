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
from app.constants import UserRole, RoutineLogStatus, ActiveStatus

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
    return {"message": "User deactivated successfully"}

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
    return {"message": "User activated successfully"}

@router.delete("/users/{user_id}")
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
    return {"message": "User deleted successfully"}

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
    settings = db.query(Settings).all()
    
    # Initialize default settings if they don't exist
    default_settings = {
        "registration_enabled": ("true", "Enable/disable user registration"),
        "max_pets_per_user": ("3", "Maximum pets allowed per user (free plan)"),
        "max_routines_per_pet": ("10", "Maximum routine tasks per pet")
    }
    
    for key, (value, description) in default_settings.items():
        setting = db.query(Settings).filter(Settings.key == key).first()
        if not setting:
            setting = Settings(key=key, value=value, description=description)
            db.add(setting)
    
    db.commit()
    
    return db.query(Settings).all()

@router.patch("/settings/{key}", response_model=SettingsResponse)
def update_setting(
    key: str,
    setting_update: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a setting"""
    setting = db.query(Settings).filter(Settings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.value = setting_update.value
    setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)
    
    return setting
