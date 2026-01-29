from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, RoutineTask, Routine
from app.schemas import RoutineTaskCreate, RoutineTaskUpdate, RoutineTaskResponse
from app.auth import get_current_user
from app.domain.reminder_service import reminder_service

router = APIRouter()

def add_pet_id_to_task(task: RoutineTask, db: Session) -> dict:
    """Helper function to add pet_id to task response"""
    routine = db.query(Routine).filter(Routine.id == task.routine_id).first()
    task_dict = {
        "id": task.id,
        "routine_id": task.routine_id,
        "pet_id": routine.pet_id if routine else None,
        "type": task.type,
        "frequency": task.frequency,
        "time": task.time,
        "active": task.active,
        "created_at": task.created_at,
    }
    return task_dict

@router.get("/", response_model=List[RoutineTaskResponse])
def get_routines(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all routine tasks for the current user"""
    tasks = reminder_service.get_all_tasks(current_user.id, db)
    return [add_pet_id_to_task(task, db) for task in tasks]

@router.get("/pet/{pet_id}", response_model=List[RoutineTaskResponse])
def get_routines_by_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all routine tasks for a specific pet"""
    tasks = reminder_service.get_tasks_by_pet(pet_id, current_user.id, db)
    return [add_pet_id_to_task(task, db) for task in tasks]

@router.post("/", response_model=RoutineTaskResponse, status_code=status.HTTP_201_CREATED)
def create_routine_task(task_data: RoutineTaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new routine task (adds task to pet's routine)"""
    task = reminder_service.create_task(task_data, current_user.id, db)
    return add_pet_id_to_task(task, db)

@router.get("/task/{task_id}", response_model=RoutineTaskResponse)
def get_routine_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a routine task by ID"""
    task = reminder_service.get_task_by_id(task_id, current_user.id, db)
    return add_pet_id_to_task(task, db)

@router.put("/task/{task_id}", response_model=RoutineTaskResponse)
def update_routine_task(task_id: int, task_data: RoutineTaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update an existing routine task"""
    task = reminder_service.update_task(task_id, task_data, current_user.id, db)
    return add_pet_id_to_task(task, db)

@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a routine task"""
    reminder_service.delete_task(task_id, current_user.id, db)
    return None
