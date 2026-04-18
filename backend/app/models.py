"""
Database models for LaNature application.

This module defines all SQLAlchemy ORM models representing database tables.
Models follow a clear hierarchy: User -> Pet -> Routine -> RoutineTask -> RoutineLog

Architectural decisions:
- Using SQLAlchemy ORM for type safety and relationship management
- Cascade deletes ensure data consistency (deleting a pet deletes its routines)
- One routine per pet design simplifies routine management
- Separate Reminder entity for future notification system expansion
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, Time, Float, Text, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base
from app.constants import RoutineLogStatus as RoutineLogStatusEnum


# ============================================================================
# ENUMS
# ============================================================================
# Note: These enums are defined here for SQLAlchemy compatibility.
# Application code should import from app.constants for consistency.

class ReminderType(str, enum.Enum):
    """
    Reminder type enum for database storage.
    
    Decision: Defined here for SQLAlchemy Enum column compatibility.
    Application code should import ReminderType from app.constants.
    """
    MEDICATION = "MEDICATION"
    FEEDING = "FEEDING"
    WATER = "WATER"
    CLEANING = "CLEANING"
    CUSTOM = "CUSTOM"


class Frequency(str, enum.Enum):
    """
    Frequency enum for database storage.
    
    Decision: Defined here for SQLAlchemy Enum column compatibility.
    Application code should import Frequency from app.constants.
    """
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


class ReminderLogStatus(str, enum.Enum):
    """
    Reminder log status enum for database storage.
    
    Decision: Defined here for SQLAlchemy Enum column compatibility.
    Application code should import ReminderLogStatus from app.constants.
    """
    PENDING = "PENDING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"


class SubscriptionStatus(str, enum.Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"


class User(Base):
    """
    User model representing application users.
    
    Role system:
    - is_superuser=False: Standard USER role (can manage own pets/routines)
    - is_superuser=True: ADMIN role (can manage all users and system settings)
    
    Decision: Using boolean is_superuser instead of role enum for simplicity.
    Can be migrated to role enum in future if more roles are needed.
    The UserRole enum in constants.py provides the conceptual mapping.
    
    Security: Password is stored as bcrypt hash, never as plain text.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # bcrypt hashed password
    is_active = Column(Boolean, default=True, nullable=False)  # Account activation status
    is_superuser = Column(Boolean, default=False, nullable=False)  # ADMIN role flag
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 2FA (Two-Factor Authentication) fields - Phase 2
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)  # 2FA status
    totp_secret = Column(String, nullable=True)  # TOTP secret key (base32 encoded)
    backup_codes = Column(JSON, default=[], nullable=False)  # List of backup recovery codes
    last_2fa_verification = Column(DateTime(timezone=True), nullable=True)  # Last successful 2FA verification

    # Relationship: One user can have many pets
    # Cascade delete: Deleting user deletes all their pets and related data
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")

class Pet(Base):
    """
    Pet model representing a user's pet.

    Each pet belongs to one user and has one routine (container for tasks).
    Optional fields allow gradual profile completion without forcing all data upfront.

    Decision: One routine per pet simplifies management - users don't need to
    create routines manually, they're auto-created with the pet.
    """
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # e.g., "dog", "cat", "bird"
    breed = Column(String, nullable=True)  # Optional breed information
    birth_date = Column(Date, nullable=True)  # Optional for age calculation
    weight = Column(Float, nullable=True)  # Optional weight tracking
    notes = Column(Text, nullable=True)  # Optional additional information
    image_url = Column(String, nullable=True)  # Path to pet's profile image (Phase 5)
    image_updated_at = Column(DateTime, nullable=True)  # Last image upload/update timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="pets")
    # One routine per pet (uselist=False) - auto-created when pet is created
    routine = relationship("Routine", back_populates="pet", uselist=False, cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="pet", cascade="all, delete-orphan")

class Routine(Base):
    """
    Routine model - container for routine tasks.
    
    One routine per pet design simplifies the mental model: each pet has
    one routine containing multiple tasks. The unique constraint on pet_id
    enforces this at the database level.
    
    Decision: Container pattern allows grouping related tasks while keeping
    task management flexible (add/remove tasks without affecting routine).
    """
    __tablename__ = "routines"
    
    id = Column(Integer, primary_key=True, index=True)
    # Unique constraint ensures one routine per pet
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    pet = relationship("Pet", back_populates="routine")
    # Cascade delete: Deleting routine deletes all its tasks
    tasks = relationship("RoutineTask", back_populates="routine", cascade="all, delete-orphan")

class RoutineTask(Base):
    """
    Routine task model representing individual care tasks within a routine.
    
    Each routine (one per pet) can have multiple tasks (feeding, medication, etc.).
    
    Decision: Using String for type/frequency instead of enum allows flexibility
    for custom task types while constants.py provides standard values.
    
    Active flag: Allows temporarily disabling tasks without deletion, preserving history.
    """
    __tablename__ = "routine_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id"), nullable=False)
    type = Column(String, nullable=False)  # Use RoutineTaskType enum values from constants
    frequency = Column(String, nullable=False)  # Use FrequencyType enum values from constants
    time = Column(Time, nullable=False)  # HH:MM format
    active = Column(Boolean, default=True, nullable=False)  # Use ActiveStatus.ACTIVE from constants
    created_at = Column(DateTime, default=datetime.utcnow)
    
    routine = relationship("Routine", back_populates="tasks")
    # Cascade delete: Deleting task deletes all its logs
    logs = relationship("RoutineLog", back_populates="task", cascade="all, delete-orphan")

class RoutineLog(Base):
    """
    Routine log model tracking completion of routine tasks.
    
    Stores historical records of when tasks were completed or skipped.
    One log entry per task per date (upsert behavior in service layer).
    
    Decision: Using String instead of enum for status allows flexibility,
    but application code should use RoutineLogStatus enum from constants.
    Status values: "done", "skipped", "pending" (see RoutineLogStatus enum).
    
    Note: task_id (not routine_id) provides granular tracking at task level.
    """
    __tablename__ = "routine_logs"
    __table_args__ = (
        UniqueConstraint("task_id", "date", name="uq_routine_log_task_date"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("routine_tasks.id"), nullable=False)
    date = Column(Date, nullable=False)
    # Status values: Use RoutineLogStatus enum (done, skipped, pending)
    status = Column(
        SQLEnum(
            RoutineLogStatusEnum,
            name="routine_log_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=False
    )
    
    task = relationship("RoutineTask", back_populates="logs")

class Reminder(Base):
    """
    Reminder model for scheduled pet care reminders.
    
    Separate from RoutineTask to support future notification system.
    Reminders can be scheduled with custom days_of_week for flexible scheduling.
    
    Decision: Using SQLEnum for type safety at database level, imported from constants.
    JSON days_of_week allows custom weekly schedules (e.g., [1,3,5] for Mon/Wed/Fri).
    
    Future: This entity can be extended with notification channels (email, SMS, push).
    """
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    # Use ReminderType enum from constants
    reminder_type = Column(SQLEnum(ReminderType), nullable=False)
    # Use Frequency enum from constants
    frequency = Column(SQLEnum(Frequency), nullable=False)
    time = Column(Time, nullable=False)  # HH:MM format
    # Custom days: [0,1,2,3,4,5,6] where 0=Monday, null means all days
    days_of_week = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)  # Use ActiveStatus from constants
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    pet = relationship("Pet", back_populates="reminders")
    logs = relationship("ReminderLog", back_populates="reminder", cascade="all, delete-orphan")

class ReminderLog(Base):
    """
    Reminder log model tracking execution of reminders.
    
    Each scheduled reminder generates log entries with execution status.
    executed_at is set when status changes to DONE, null for PENDING/SKIPPED.
    
    Decision: Using SQLEnum ensures database-level validation of status values.
    Status enum imported from constants for consistency.
    """
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)  # When reminder was scheduled to fire
    executed_at = Column(DateTime, nullable=True)  # When executed (null if PENDING/SKIPPED)
    # Use ReminderLogStatus enum from constants (PENDING, DONE, SKIPPED)
    status = Column(SQLEnum(ReminderLogStatus), nullable=False)
    
    reminder = relationship("Reminder", back_populates="logs")

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RefreshToken(Base):
    """Refresh tokens for extended session management - Phase 2 Part 3"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)  # Hash of refresh token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)  # For logout
    revoked_at = Column(DateTime(timezone=True), nullable=True)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    """Audit logs for GDPR compliance and security tracking - Phase 2 Part 5"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for system actions
    action = Column(String, nullable=False, index=True)  # login_success, login_failed, password_changed, profile_updated, account_deleted
    resource_type = Column(String, nullable=True)  # user, pet, routine, etc
    resource_id = Column(Integer, nullable=True)
    details = Column(String, nullable=True)  # JSON string with additional details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)  # free/pro
    name = Column(String, nullable=False)
    monthly_price_cents = Column(Integer, nullable=False)
    trial_days = Column(Integer, nullable=False, default=0)
    max_pets = Column(Integer, nullable=False, default=3)
    max_routines_per_pet = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    current_period_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_period_end = Column(DateTime, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    provider = Column(String, nullable=True)  # e.g. stripe
    provider_subscription_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    events = relationship("BillingEvent", back_populates="subscription", cascade="all, delete-orphan")


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # payment_succeeded/payment_failed/plan_changed
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscription = relationship("UserSubscription", back_populates="events")
