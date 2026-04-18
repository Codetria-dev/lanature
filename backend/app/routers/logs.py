"""
Routine logs router with pagination - Phase 5 Performance Optimization

Handles routine task logs with:
- Pagination support (large history datasets)
- Caching for frequently accessed logs
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RoutineLogCreate, RoutineLogResponse
from app.auth import get_current_user
from app.domain.reminder_service import reminder_service
from app.pagination import paginate, PaginationParams

router = APIRouter()


@router.get("/")
def get_logs(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all logs for the current user with pagination.

    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 10, max: 100)

    **Performance:** Important for large history datasets (supports pagination)
    """
    query = reminder_service.get_all_logs_query(current_user.id, db)
    result = paginate(query, params.page, params.limit)

    return {
        "data": result["data"],
        "pagination": result["pagination"]
    }


@router.get("/task/{task_id}")
def get_logs_by_task(
    task_id: int,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all logs for a specific routine task with pagination.

    **Performance:** Validates task ownership before returning logs
    """
    query = reminder_service.get_logs_by_task_query(task_id, current_user.id, db)
    result = paginate(query, params.page, params.limit)

    return {
        "data": result["data"],
        "pagination": result["pagination"]
    }


@router.get("/pet/{pet_id}")
def get_logs_by_pet(
    pet_id: int,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all logs for a specific pet with pagination.

    **Performance:** Validates pet ownership before returning logs
    """
    query = reminder_service.get_logs_by_pet_query(pet_id, current_user.id, db)
    result = paginate(query, params.page, params.limit)

    return {
        "data": result["data"],
        "pagination": result["pagination"]
    }


@router.post("/", response_model=RoutineLogResponse, status_code=status.HTTP_201_CREATED)
def create_log(
    log_data: RoutineLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task log entry."""
    return reminder_service.create_log(log_data, current_user.id, db)


@router.get("/{log_id}", response_model=RoutineLogResponse)
def get_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific log entry by ID."""
    return reminder_service.get_log_by_id(log_id, current_user.id, db)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a log entry."""
    reminder_service.delete_log(log_id, current_user.id, db)
    return None
