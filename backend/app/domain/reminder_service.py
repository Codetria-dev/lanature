from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List
from datetime import datetime
from app.models import Routine, RoutineTask, Pet, RoutineLog, Reminder, ReminderLog
from app.schemas import RoutineTaskCreate, RoutineTaskUpdate, RoutineLogCreate, ReminderCreate, ReminderUpdate, ReminderLogCreate, ReminderLogUpdate
from app.domain.settings_service import settings_service
from app.domain.billing_service import billing_service


class ReminderService:
    @staticmethod
    def verify_pet_ownership(pet_id: int, user_id: int, db: Session) -> Pet:
        """Verify that a pet belongs to the user"""
        pet = db.query(Pet).filter(Pet.id == pet_id, Pet.user_id == user_id).first()
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found"
            )
        return pet

    @staticmethod
    def get_or_create_routine(pet_id: int, user_id: int, db: Session) -> Routine:
        """Get or create a routine for a pet (one routine per pet)"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        
        routine = db.query(Routine).filter(Routine.pet_id == pet_id).first()
        if not routine:
            routine = Routine(pet_id=pet_id)
            db.add(routine)
            db.commit()
            db.refresh(routine)
        return routine

    @staticmethod
    def verify_routine_task_ownership(task_id: int, user_id: int, db: Session) -> RoutineTask:
        """Verify that a routine task belongs to the user"""
        task = db.query(RoutineTask).join(Routine).join(Pet).filter(
            RoutineTask.id == task_id,
            Pet.user_id == user_id
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine task not found"
            )
        return task

    @staticmethod
    def get_all_tasks(user_id: int, db: Session) -> List[RoutineTask]:
        """Get all routine tasks for a user"""
        return db.query(RoutineTask).join(Routine).join(Pet).filter(Pet.user_id == user_id).all()

    @staticmethod
    def get_tasks_by_pet(pet_id: int, user_id: int, db: Session) -> List[RoutineTask]:
        """Get all routine tasks for a specific pet"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        routine = ReminderService.get_or_create_routine(pet_id, user_id, db)
        return db.query(RoutineTask).filter(RoutineTask.routine_id == routine.id).all()

    @staticmethod
    def get_task_by_id(task_id: int, user_id: int, db: Session) -> RoutineTask:
        """Get a routine task by ID, ensuring it belongs to the user"""
        return ReminderService.verify_routine_task_ownership(task_id, user_id, db)

    @staticmethod
    def create_task(task_data: RoutineTaskCreate, user_id: int, db: Session) -> RoutineTask:
        """Create a new routine task (adds task to pet's routine)"""
        settings_service.ensure_defaults(db)
        _, max_routines_per_pet = billing_service.get_limits(db, user_id)
        if max_routines_per_pet <= 0:
            max_routines_per_pet = settings_service.get_int(db, "max_routines_per_pet", 10)

        routine = ReminderService.get_or_create_routine(task_data.pet_id, user_id, db)
        tasks_count = db.query(RoutineTask).filter(RoutineTask.routine_id == routine.id).count()
        if tasks_count >= max_routines_per_pet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum routine tasks per pet reached ({max_routines_per_pet})",
            )
        
        task = RoutineTask(
            routine_id=routine.id,
            type=task_data.type,
            frequency=task_data.frequency,
            time=task_data.time,
            active=task_data.active
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(task_id: int, task_data: RoutineTaskUpdate, user_id: int, db: Session) -> RoutineTask:
        """Update an existing routine task"""
        task = ReminderService.get_task_by_id(task_id, user_id, db)
        
        if task_data.type is not None:
            task.type = task_data.type
        if task_data.frequency is not None:
            task.frequency = task_data.frequency
        if task_data.time is not None:
            task.time = task_data.time
        if task_data.active is not None:
            task.active = task_data.active
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(task_id: int, user_id: int, db: Session) -> None:
        """Delete a routine task"""
        task = ReminderService.get_task_by_id(task_id, user_id, db)
        db.delete(task)
        db.commit()

    # RoutineLog methods
    @staticmethod
    def get_all_logs(user_id: int, db: Session) -> List[RoutineLog]:
        """Get all logs for a user"""
        return db.query(RoutineLog).join(RoutineTask).join(Routine).join(Pet).filter(
            Pet.user_id == user_id
        ).all()

    @staticmethod
    def get_logs_by_task(task_id: int, user_id: int, db: Session) -> List[RoutineLog]:
        """Get all logs for a specific routine task"""
        ReminderService.verify_routine_task_ownership(task_id, user_id, db)
        return db.query(RoutineLog).filter(RoutineLog.task_id == task_id).all()

    @staticmethod
    def get_logs_by_pet(pet_id: int, user_id: int, db: Session) -> List[RoutineLog]:
        """Get all logs for a specific pet"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        return db.query(RoutineLog).join(RoutineTask).join(Routine).filter(Routine.pet_id == pet_id).all()

    @staticmethod
    def get_log_by_id(log_id: int, user_id: int, db: Session) -> RoutineLog:
        """Get a log by ID, ensuring it belongs to the user"""
        log = db.query(RoutineLog).join(RoutineTask).join(Routine).join(Pet).filter(
            RoutineLog.id == log_id,
            Pet.user_id == user_id
        ).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log not found"
            )
        return log

    @staticmethod
    def create_log(log_data: RoutineLogCreate, user_id: int, db: Session) -> RoutineLog:
        """Create or update a routine log"""
        ReminderService.verify_routine_task_ownership(log_data.task_id, user_id, db)
        
        # Check if log already exists for this task and date
        existing_log = db.query(RoutineLog).filter(
            RoutineLog.task_id == log_data.task_id,
            RoutineLog.date == log_data.date
        ).first()
        
        if existing_log:
            # Update existing log
            existing_log.status = log_data.status
            db.commit()
            db.refresh(existing_log)
            return existing_log
        
        # Create new log
        log = RoutineLog(
            task_id=log_data.task_id,
            date=log_data.date,
            status=log_data.status
        )
        db.add(log)
        try:
            db.commit()
        except IntegrityError:
            # Another concurrent request inserted the same (task_id, date).
            # Roll back and apply the update to the now-existing row.
            db.rollback()
            existing_log = db.query(RoutineLog).filter(
                RoutineLog.task_id == log_data.task_id,
                RoutineLog.date == log_data.date
            ).first()
            if not existing_log:
                raise
            existing_log.status = log_data.status
            db.commit()
            db.refresh(existing_log)
            return existing_log
        db.refresh(log)
        return log

    @staticmethod
    def delete_log(log_id: int, user_id: int, db: Session) -> None:
        """Delete a routine log"""
        log = ReminderService.get_log_by_id(log_id, user_id, db)
        db.delete(log)
        db.commit()

    # Phase 5: Query methods for pagination
    @staticmethod
    def get_all_logs_query(user_id: int, db: Session):
        """Get query for all logs for a user (for pagination)"""
        return db.query(RoutineLog).join(RoutineTask).join(Routine).join(Pet).filter(
            Pet.user_id == user_id
        ).order_by(RoutineLog.date.desc())

    @staticmethod
    def get_logs_by_task_query(task_id: int, user_id: int, db: Session):
        """Get query for logs by task (for pagination)"""
        ReminderService.verify_routine_task_ownership(task_id, user_id, db)
        return db.query(RoutineLog).filter(RoutineLog.task_id == task_id).order_by(RoutineLog.date.desc())

    @staticmethod
    def get_logs_by_pet_query(pet_id: int, user_id: int, db: Session):
        """Get query for logs by pet (for pagination)"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        return db.query(RoutineLog).join(RoutineTask).join(Routine).filter(
            Routine.pet_id == pet_id
        ).order_by(RoutineLog.date.desc())

    # Reminder methods (new entity)
    @staticmethod
    def verify_reminder_ownership(reminder_id: int, user_id: int, db: Session) -> Reminder:
        """Verify that a reminder belongs to the user"""
        reminder = db.query(Reminder).join(Pet).filter(
            Reminder.id == reminder_id,
            Pet.user_id == user_id
        ).first()
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        return reminder

    @staticmethod
    def get_all_reminders(user_id: int, db: Session) -> List[Reminder]:
        """Get all reminders for a user"""
        return db.query(Reminder).join(Pet).filter(Pet.user_id == user_id).all()

    @staticmethod
    def get_reminders_by_pet(pet_id: int, user_id: int, db: Session) -> List[Reminder]:
        """Get all reminders for a specific pet"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        return db.query(Reminder).filter(Reminder.pet_id == pet_id).all()

    @staticmethod
    def get_reminder_by_id(reminder_id: int, user_id: int, db: Session) -> Reminder:
        """Get a reminder by ID, ensuring it belongs to the user"""
        return ReminderService.verify_reminder_ownership(reminder_id, user_id, db)

    @staticmethod
    def create_reminder(reminder_data: ReminderCreate, user_id: int, db: Session) -> Reminder:
        """Create a new reminder"""
        ReminderService.verify_pet_ownership(reminder_data.pet_id, user_id, db)
        
        reminder = Reminder(
            pet_id=reminder_data.pet_id,
            title=reminder_data.title,
            description=reminder_data.description,
            reminder_type=reminder_data.reminder_type,
            frequency=reminder_data.frequency,
            time=reminder_data.time,
            days_of_week=reminder_data.days_of_week,
            is_active=reminder_data.is_active
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def update_reminder(reminder_id: int, reminder_data: ReminderUpdate, user_id: int, db: Session) -> Reminder:
        """Update an existing reminder"""
        reminder = ReminderService.get_reminder_by_id(reminder_id, user_id, db)
        
        if reminder_data.title is not None:
            reminder.title = reminder_data.title
        if reminder_data.description is not None:
            reminder.description = reminder_data.description
        if reminder_data.reminder_type is not None:
            reminder.reminder_type = reminder_data.reminder_type
        if reminder_data.frequency is not None:
            reminder.frequency = reminder_data.frequency
        if reminder_data.time is not None:
            reminder.time = reminder_data.time
        if reminder_data.days_of_week is not None:
            reminder.days_of_week = reminder_data.days_of_week
        if reminder_data.is_active is not None:
            reminder.is_active = reminder_data.is_active
        
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def delete_reminder(reminder_id: int, user_id: int, db: Session) -> None:
        """Delete a reminder"""
        reminder = ReminderService.get_reminder_by_id(reminder_id, user_id, db)
        db.delete(reminder)
        db.commit()

    # ReminderLog methods
    @staticmethod
    def get_all_reminder_logs(user_id: int, db: Session) -> List[ReminderLog]:
        """Get all reminder logs for a user"""
        return db.query(ReminderLog).join(Reminder).join(Pet).filter(
            Pet.user_id == user_id
        ).all()

    @staticmethod
    def get_reminder_logs_by_reminder(reminder_id: int, user_id: int, db: Session) -> List[ReminderLog]:
        """Get all logs for a specific reminder"""
        ReminderService.verify_reminder_ownership(reminder_id, user_id, db)
        return db.query(ReminderLog).filter(ReminderLog.reminder_id == reminder_id).all()

    @staticmethod
    def get_reminder_logs_by_pet(pet_id: int, user_id: int, db: Session) -> List[ReminderLog]:
        """Get all reminder logs for a specific pet"""
        ReminderService.verify_pet_ownership(pet_id, user_id, db)
        return db.query(ReminderLog).join(Reminder).filter(Reminder.pet_id == pet_id).all()

    @staticmethod
    def get_reminder_log_by_id(log_id: int, user_id: int, db: Session) -> ReminderLog:
        """Get a reminder log by ID, ensuring it belongs to the user"""
        log = db.query(ReminderLog).join(Reminder).join(Pet).filter(
            ReminderLog.id == log_id,
            Pet.user_id == user_id
        ).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder log not found"
            )
        return log

    @staticmethod
    def create_reminder_log(log_data: ReminderLogCreate, user_id: int, db: Session) -> ReminderLog:
        """Create a new reminder log"""
        ReminderService.verify_reminder_ownership(log_data.reminder_id, user_id, db)
        
        # If status is DONE and executed_at is not provided, set it to now
        executed_at = log_data.executed_at
        if log_data.status.value == "DONE" and executed_at is None:
            executed_at = datetime.utcnow()
        
        log = ReminderLog(
            reminder_id=log_data.reminder_id,
            scheduled_at=log_data.scheduled_at,
            executed_at=executed_at,
            status=log_data.status
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update_reminder_log(log_id: int, log_data: ReminderLogUpdate, user_id: int, db: Session) -> ReminderLog:
        """Update an existing reminder log"""
        log = ReminderService.get_reminder_log_by_id(log_id, user_id, db)
        
        if log_data.status is not None:
            log.status = log_data.status
            # If status is changed to DONE and executed_at is not provided, set it to now
            if log_data.status.value == "DONE" and log.executed_at is None:
                log.executed_at = log_data.executed_at or datetime.utcnow()
        
        if log_data.executed_at is not None:
            log.executed_at = log_data.executed_at
        
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def delete_reminder_log(log_id: int, user_id: int, db: Session) -> None:
        """Delete a reminder log"""
        log = ReminderService.get_reminder_log_by_id(log_id, user_id, db)
        db.delete(log)
        db.commit()


# Create a singleton instance
reminder_service = ReminderService()
