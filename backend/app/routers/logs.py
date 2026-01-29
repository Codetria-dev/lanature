from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import RoutineLogCreate, RoutineLogResponse
from app.auth import get_current_user
from app.domain.reminder_service import reminder_service

router = APIRouter()

@router.get("/", response_model=List[RoutineLogResponse])
def get_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return reminder_service.get_all_logs(current_user.id, db)

@router.get("/task/{task_id}", response_model=List[RoutineLogResponse])
def get_logs_by_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all logs for a specific routine task"""
    return reminder_service.get_logs_by_task(task_id, current_user.id, db)

@router.get("/pet/{pet_id}", response_model=List[RoutineLogResponse])
def get_logs_by_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return reminder_service.get_logs_by_pet(pet_id, current_user.id, db)

@router.post("/", response_model=RoutineLogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log_data: RoutineLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return reminder_service.create_log(log_data, current_user.id, db)

@router.get("/{log_id}", response_model=RoutineLogResponse)
def get_log(log_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return reminder_service.get_log_by_id(log_id, current_user.id, db)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder_service.delete_log(log_id, current_user.id, db)
    return None
