from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import PetCreate, PetUpdate, PetResponse
from app.auth import get_current_user
from app.domain.pet_service import pet_service

router = APIRouter()

@router.get("/", response_model=List[PetResponse])
def get_pets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return pet_service.get_all(current_user.id, db)

@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(pet_data: PetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return pet_service.create(pet_data, current_user.id, db)

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return pet_service.get_by_id(pet_id, current_user.id, db)

@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(pet_id: int, pet_data: PetUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return pet_service.update(pet_id, pet_data, current_user.id, db)

@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet_service.delete(pet_id, current_user.id, db)
    return None
