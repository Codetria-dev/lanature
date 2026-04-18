from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models import Pet, Routine
from app.schemas import PetCreate, PetUpdate
from app.domain.settings_service import settings_service
from app.domain.billing_service import billing_service


class PetService:
    @staticmethod
    def get_all(user_id: int, db: Session) -> List[Pet]:
        """Get all pets for a user"""
        return db.query(Pet).filter(Pet.user_id == user_id).all()

    @staticmethod
    def get_by_id(pet_id: int, user_id: int, db: Session) -> Pet:
        """Get a pet by ID, ensuring it belongs to the user"""
        pet = db.query(Pet).filter(Pet.id == pet_id, Pet.user_id == user_id).first()
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found"
            )
        return pet

    @staticmethod
    def create(pet_data: PetCreate, user_id: int, db: Session) -> Pet:
        """Create a new pet and automatically create a routine for it"""
        settings_service.ensure_defaults(db)
        max_pets_per_user, _ = billing_service.get_limits(db, user_id)
        if max_pets_per_user <= 0:
            max_pets_per_user = settings_service.get_int(db, "max_pets_per_user", 3)

        pets_count = db.query(Pet).filter(Pet.user_id == user_id).count()
        if pets_count >= max_pets_per_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum pets per user reached ({max_pets_per_user})",
            )

        pet = Pet(
            user_id=user_id,
            name=pet_data.name,
            species=pet_data.species,
            breed=pet_data.breed,
            birth_date=pet_data.birth_date,
            weight=pet_data.weight,
            notes=pet_data.notes
        )
        db.add(pet)
        db.flush()  # Flush to get pet.id
        
        # Create routine for the pet
        routine = Routine(pet_id=pet.id)
        db.add(routine)
        
        db.commit()
        db.refresh(pet)
        return pet

    @staticmethod
    def update(pet_id: int, pet_data: PetUpdate, user_id: int, db: Session) -> Pet:
        """Update an existing pet"""
        pet = PetService.get_by_id(pet_id, user_id, db)
        
        if pet_data.name is not None:
            pet.name = pet_data.name
        if pet_data.species is not None:
            pet.species = pet_data.species
        if pet_data.breed is not None:
            pet.breed = pet_data.breed
        if pet_data.birth_date is not None:
            pet.birth_date = pet_data.birth_date
        if pet_data.weight is not None:
            pet.weight = pet_data.weight
        if pet_data.notes is not None:
            pet.notes = pet_data.notes
        
        db.commit()
        db.refresh(pet)
        return pet

    @staticmethod
    def delete(pet_id: int, user_id: int, db: Session) -> None:
        """Delete a pet"""
        pet = PetService.get_by_id(pet_id, user_id, db)
        db.delete(pet)
        db.commit()


# Create a singleton instance
pet_service = PetService()
