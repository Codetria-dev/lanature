"""
Analytics service for usage metrics and insights - Phase 4 Data & Analytics

Provides metrics on:
- User activity (tasks completed, completion rates)
- Pet-specific analytics
- Historical trends
- Engagement streaks
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models import Pet, RoutineTask, RoutineLog, Reminder, ReminderLog
from app.constants import RoutineLogStatus


class AnalyticsService:
    """Service for calculating and retrieving analytics metrics."""

    @staticmethod
    def get_overview(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive overview of user's pet care metrics.

        Returns:
            {
                "total_pets": 5,
                "total_routines": 5,
                "tasks_completed_today": 3,
                "tasks_pending": 2,
                "completion_rate": 85.5,
                "streak_days": 12,
                "most_active_pet": "Max",
                "this_week": {
                    "tasks_completed": 18,
                    "tasks_scheduled": 20
                }
            }
        """
        # Get pet and routine counts
        pet_count = db.query(func.count(Pet.id)).filter(
            Pet.user_id == user_id
        ).scalar() or 0

        routine_count = db.query(func.count(RoutineTask.id)).filter(
            RoutineTask.routine_id.in_(
                db.query(RoutineTask.routine_id).join(
                    Pet, RoutineTask.routine_id == Pet.routine.property.key
                ).filter(Pet.user_id == user_id)
            )
        ).scalar() or 0

        # Today's tasks
        today = date.today()
        today_logs = db.query(RoutineLog).filter(
            and_(
                RoutineLog.date == today,
                RoutineLog.task_id.in_(
                    db.query(RoutineTask.id).filter(RoutineTask.active == True)
                )
            )
        ).all()

        tasks_completed = sum(1 for log in today_logs if log.status == RoutineLogStatus.DONE.value)
        tasks_pending = sum(1 for log in today_logs if log.status == RoutineLogStatus.PENDING.value)

        # Completion rate
        total_tasks_today = len(today_logs)
        completion_rate = (tasks_completed / total_tasks_today * 100) if total_tasks_today > 0 else 0

        # Streak calculation
        streak_days = AnalyticsService._calculate_streak(user_id, db)

        # Most active pet
        most_active_pet = AnalyticsService._get_most_active_pet(user_id, db)

        # This week stats
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_logs = db.query(RoutineLog).filter(
            and_(
                RoutineLog.date >= week_start,
                RoutineLog.task_id.in_(
                    db.query(RoutineTask.id).filter(RoutineTask.active == True)
                )
            )
        ).all()

        week_completed = sum(1 for log in week_logs if log.status == RoutineLogStatus.DONE.value)
        week_scheduled = len(week_logs)

        return {
            "total_pets": pet_count,
            "total_routines": routine_count,
            "tasks_completed_today": tasks_completed,
            "tasks_pending": tasks_pending,
            "completion_rate": round(completion_rate, 1),
            "streak_days": streak_days,
            "most_active_pet": most_active_pet,
            "this_week": {
                "tasks_completed": week_completed,
                "tasks_scheduled": week_scheduled,
            },
        }

    @staticmethod
    def get_pet_analytics(pet_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get analytics for a specific pet.

        Returns metrics on task completion by type and date.
        """
        pet = db.query(Pet).filter(
            and_(Pet.id == pet_id, Pet.user_id == user_id)
        ).first()

        if not pet:
            return {}

        # Total tasks and completion
        routine = pet.routine
        if not routine or not routine.tasks:
            return {
                "pet_name": pet.name,
                "total_tasks": 0,
                "completed": 0,
                "completion_rate": 0,
                "tasks_by_type": {},
                "this_month": {
                    "completed": 0,
                    "pending": 0,
                    "skipped": 0,
                },
            }

        task_ids = [t.id for t in routine.tasks]
        all_logs = db.query(RoutineLog).filter(
            RoutineLog.task_id.in_(task_ids)
        ).all()

        total_logs = len(all_logs)
        completed = sum(1 for log in all_logs if log.status == RoutineLogStatus.DONE.value)
        completion_rate = (completed / total_logs * 100) if total_logs > 0 else 0

        # Tasks by type
        tasks_by_type = {}
        for task in routine.tasks:
            task_logs = [log for log in all_logs if log.task_id == task.id]
            count = sum(1 for log in task_logs if log.status == RoutineLogStatus.DONE.value)
            tasks_by_type[task.type] = count

        # This month
        month_start = date.today().replace(day=1)
        month_logs = [log for log in all_logs if log.date >= month_start]
        month_completed = sum(1 for log in month_logs if log.status == RoutineLogStatus.DONE.value)
        month_pending = sum(1 for log in month_logs if log.status == RoutineLogStatus.PENDING.value)
        month_skipped = sum(1 for log in month_logs if log.status == RoutineLogStatus.SKIPPED.value)

        return {
            "pet_name": pet.name,
            "total_tasks": total_logs,
            "completed": completed,
            "completion_rate": round(completion_rate, 1),
            "tasks_by_type": tasks_by_type,
            "this_month": {
                "completed": month_completed,
                "pending": month_pending,
                "skipped": month_skipped,
            },
        }

    @staticmethod
    def get_history(user_id: int, db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get historical data for the past N days.

        Returns daily completion data and trend.
        """
        daily_data = []
        today = date.today()

        for i in range(days):
            current_date = today - timedelta(days=i)
            logs = db.query(RoutineLog).filter(
                RoutineLog.date == current_date
            ).all()

            completed = sum(1 for log in logs if log.status == RoutineLogStatus.DONE.value)
            scheduled = len(logs)

            daily_data.insert(0, {
                "date": current_date.isoformat(),
                "completed": completed,
                "scheduled": scheduled,
            })

        # Calculate trend
        if len(daily_data) >= 2:
            first_week = daily_data[:7]
            last_week = daily_data[-7:]

            first_avg = sum(d["completed"] for d in first_week) / len(first_week) if first_week else 0
            last_avg = sum(d["completed"] for d in last_week) / len(last_week) if last_week else 0

            if last_avg > first_avg * 1.1:
                trend = "up"
            elif last_avg < first_avg * 0.9:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"

        avg_completion_rate = (
            sum(d["completed"] for d in daily_data) /
            max(1, sum(d["scheduled"] for d in daily_data)) * 100
            if daily_data else 0
        )

        return {
            "daily_data": daily_data,
            "trend": trend,
            "avg_completion_rate": round(avg_completion_rate, 1),
        }

    @staticmethod
    def _calculate_streak(user_id: int, db: Session) -> int:
        """Calculate consecutive days with all tasks completed."""
        today = date.today()
        streak = 0

        for days_back in range(365):  # Max 1 year
            check_date = today - timedelta(days=days_back)

            # Get all logs for this date
            logs = db.query(RoutineLog).filter(
                RoutineLog.date == check_date
            ).all()

            if not logs:
                break  # No data for this date, streak ends

            # Check if all tasks completed
            completed = sum(1 for log in logs if log.status == RoutineLogStatus.DONE.value)
            if completed == len(logs):
                streak += 1
            else:
                break  # Not all tasks completed, streak ends

        return streak

    @staticmethod
    def _get_most_active_pet(user_id: int, db: Session) -> Optional[str]:
        """Get the pet with the most completed tasks."""
        pets = db.query(Pet).filter(Pet.user_id == user_id).all()

        if not pets:
            return None

        max_completed = 0
        most_active = None

        for pet in pets:
            routine = pet.routine
            if routine and routine.tasks:
                task_ids = [t.id for t in routine.tasks]
                completed = db.query(func.count(RoutineLog.id)).filter(
                    and_(
                        RoutineLog.task_id.in_(task_ids),
                        RoutineLog.status == RoutineLogStatus.DONE.value,
                    )
                ).scalar() or 0

                if completed > max_completed:
                    max_completed = completed
                    most_active = pet.name

        return most_active


# Singleton instance
analytics_service = AnalyticsService()
