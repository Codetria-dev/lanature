"""
GDPR compliance service for data export and audit logging.

Implements data privacy and audit trail requirements.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import User, AuditLog, Pet, Routine, RoutineTask, RoutineLog


class GDPRService:
    """Service for GDPR compliance operations."""

    @staticmethod
    def create_audit_log(
        db: Session,
        action: str,
        user_id: int = None,
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        Create an audit log entry.

        Args:
            db: Database session
            action: Action performed (login_success, password_changed, etc)
            user_id: User who performed the action
            resource_type: Type of resource affected (user, pet, routine, etc)
            resource_id: ID of the affected resource
            details: Additional details as dict
            ip_address: Client IP address
            user_agent: Client user agent string
        """
        log_entry = AuditLog(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log_entry)
        db.commit()

    @staticmethod
    def export_user_data(db: Session, user: User) -> dict:
        """
        Export all data associated with a user (GDPR right to data portability).

        Args:
            db: Database session
            user: User object

        Returns:
            Dict containing all user data
        """
        # User profile
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "2fa_enabled": user.is_2fa_enabled
        }

        # Pets and related data
        pets = db.query(Pet).filter(Pet.user_id == user.id).all()
        pets_data = []

        for pet in pets:
            pet_info = {
                "id": pet.id,
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "birth_date": str(pet.birth_date) if pet.birth_date else None,
                "weight": pet.weight,
                "notes": pet.notes,
                "created_at": pet.created_at.isoformat() if pet.created_at else None
            }

            # Routines for this pet
            routines = db.query(Routine).filter(Routine.pet_id == pet.id).all()
            routines_data = []

            for routine in routines:
                routine_info = {
                    "id": routine.id,
                    "created_at": routine.created_at.isoformat() if routine.created_at else None
                }

                # Tasks in this routine
                tasks = db.query(RoutineTask).filter(RoutineTask.routine_id == routine.id).all()
                tasks_data = []

                for task in tasks:
                    task_info = {
                        "id": task.id,
                        "type": task.task_type,
                        "frequency": task.frequency,
                        "time": str(task.time) if task.time else None,
                        "is_active": task.is_active,
                        "created_at": task.created_at.isoformat() if task.created_at else None
                    }

                    # Logs for this task
                    logs = db.query(RoutineLog).filter(RoutineLog.task_id == task.id).all()
                    logs_data = [
                        {
                            "id": log.id,
                            "date": str(log.date) if log.date else None,
                            "status": log.status,
                            "created_at": log.created_at.isoformat() if log.created_at else None
                        }
                        for log in logs
                    ]

                    task_info["logs"] = logs_data
                    tasks_data.append(task_info)

                routine_info["tasks"] = tasks_data
                routines_data.append(routine_info)

            pet_info["routines"] = routines_data
            pets_data.append(pet_info)

        user_data["pets"] = pets_data

        # Audit logs for this user
        audit_logs = db.query(AuditLog).filter(AuditLog.user_id == user.id).all()
        audit_data = [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in audit_logs
        ]

        user_data["audit_logs"] = audit_data

        return user_data

    @staticmethod
    def delete_user_data(db: Session, user: User) -> bool:
        """
        Delete all user data (GDPR right to be forgotten).

        Cascades deletion to all related data.

        Args:
            db: Database session
            user: User object to delete

        Returns:
            True if successful
        """
        try:
            # Create audit log before deletion
            GDPRService.create_audit_log(
                db,
                action="account_deleted",
                user_id=user.id,
                details={"email": user.email}
            )

            # Delete user (cascades to pets, routines, logs, etc)
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def get_user_audit_logs(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get audit logs for a user.

        Args:
            db: Database session
            user_id: User ID to get logs for
            limit: Maximum number of logs to return
            offset: Number of logs to skip

        Returns:
            List of audit log dicts
        """
        logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "details": json.loads(log.details) if log.details else None
            }
            for log in logs
        ]
