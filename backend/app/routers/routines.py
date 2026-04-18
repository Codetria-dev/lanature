"""
Routine tasks router with pagination and eager loading - Phase 5 Performance Optimization

Handles routine task CRUD operations with:
- Pagination support
- Eager loading to prevent N+1 queries (previously was querying routine for each task)
- Caching for task lists
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import User, RoutineTask, Routine, Pet
from app.schemas import RoutineTaskCreate, RoutineTaskUpdate, RoutineTaskResponse
from app.auth import get_current_user
from app.domain.reminder_service import reminder_service
from app.cache import cache_manager
from app.pagination import paginate, PaginationParams

router = APIRouter()


def add_pet_id_to_task(task: RoutineTask) -> dict:
    """
    Helper function to add pet_id to task response.

    **Performance improvement:** Now uses eager-loaded routine to avoid N+1 queries
    """
    # Routine is eager-loaded, so no additional query
    pet_id = task.routine.pet_id if task.routine else None

    task_dict = {
        "id": task.id,
        "routine_id": task.routine_id,
        "pet_id": pet_id,
        "type": task.type,
        "task_type": task.type,
        "frequency": task.frequency,
        "time": task.time,
        "active": task.active,
        "is_active": task.active,
        "created_at": task.created_at,
    }
    return task_dict


@router.get("/")
def get_routines(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all routine tasks for the current user with pagination.

    **Performance:** Uses eager loading to prevent N+1 queries (1 query instead of N+1)
    """
    # Query with eager loading of routine relationships
    query = db.query(RoutineTask).join(Routine).join(Pet).filter(
        Pet.user_id == current_user.id
    ).options(
        joinedload(RoutineTask.routine)  # Eager load routine to prevent N+1
    )

    result = paginate(query, params.page, params.limit)

    # Transform data
    return {
        "data": [add_pet_id_to_task(task) for task in result["data"]],
        "pagination": result["pagination"]
    }


@router.get("/pet/{pet_id}")
def get_routines_by_pet(
    pet_id: int,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all routine tasks for a specific pet with pagination.

    **Performance:** Validates pet ownership and uses eager loading
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.user_id == current_user.id).first()
    if not pet:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pet not found")

    # Query with eager loading
    query = db.query(RoutineTask).join(Routine).filter(
        Routine.pet_id == pet_id
    ).options(
        joinedload(RoutineTask.routine)
    )

    result = paginate(query, params.page, params.limit)

    return {
        "data": [add_pet_id_to_task(task) for task in result["data"]],
        "pagination": result["pagination"]
    }


@router.post("/", response_model=RoutineTaskResponse, status_code=status.HTTP_201_CREATED)
def create_routine_task(
    task_data: RoutineTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new routine task.

    **Performance:** Invalidates task cache after creation
    """
    task = reminder_service.create_task(task_data, current_user.id, db)

    # Invalidate cache for this user
    cache_manager.invalidate_today_tasks(current_user.id)

    return add_pet_id_to_task(task)


@router.get("/task/{task_id}", response_model=RoutineTaskResponse)
def get_routine_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a routine task by ID with eager loading."""
    task = reminder_service.get_task_by_id(task_id, current_user.id, db)
    return add_pet_id_to_task(task)


@router.put("/task/{task_id}", response_model=RoutineTaskResponse)
def update_routine_task(
    task_id: int,
    task_data: RoutineTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing routine task.

    **Performance:** Invalidates cache after update
    """
    task = reminder_service.update_task(task_id, task_data, current_user.id, db)

    # Invalidate cache
    cache_manager.invalidate_today_tasks(current_user.id)

    return add_pet_id_to_task(task)


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a routine task.

    **Performance:** Invalidates cache after deletion
    """
    reminder_service.delete_task(task_id, current_user.id, db)

    # Invalidate cache
    cache_manager.invalidate_today_tasks(current_user.id)

    return None
