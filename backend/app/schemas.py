"""
Pydantic schemas for request/response validation.

This module defines all data transfer objects (DTOs) used in API endpoints.
Schemas provide automatic validation, serialization, and documentation.

Architectural decisions:
- Separate Create/Update/Response schemas for flexibility
- Using enums from constants for type safety
- Optional fields in Update schemas allow partial updates
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, List
from app.models import ReminderType, Frequency, ReminderLogStatus
from app.constants import RoutineLogStatus, UserRole

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class LoginRequest(BaseModel):
    email: str  # Changed from EmailStr to allow "admin" as username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Pet Schemas
class PetCreate(BaseModel):
    name: str
    species: str  # dog, cat, bird, etc
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    weight: Optional[float] = None
    notes: Optional[str] = None

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    weight: Optional[float] = None
    notes: Optional[str] = None

class PetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    species: str
    breed: Optional[str]
    birth_date: Optional[date]
    weight: Optional[float]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Routine Schemas (container - one per pet)
class RoutineResponse(BaseModel):
    id: int
    pet_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# RoutineTask Schemas (tasks within a routine)
class RoutineTaskCreate(BaseModel):
    pet_id: int  # Pet ID to find/create routine
    type: str
    frequency: str
    time: time
    active: bool = True

class RoutineTaskUpdate(BaseModel):
    type: Optional[str] = None
    frequency: Optional[str] = None
    time: Optional[time] = None
    active: Optional[bool] = None

class RoutineTaskResponse(BaseModel):
    id: int
    routine_id: int
    pet_id: int  # Added for frontend convenience
    type: str
    frequency: str
    time: time
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# RoutineLog Schemas
class RoutineLogCreate(BaseModel):
    """Schema for creating routine log entries."""
    task_id: int
    date: date
    # Use RoutineLogStatus enum values: "done", "skipped", "pending"
    status: str

class RoutineLogResponse(BaseModel):
    """Schema for routine log responses."""
    id: int
    task_id: int
    date: date
    # Status from RoutineLogStatus enum
    status: str
    
    class Config:
        from_attributes = True

# Reminder Schemas
class ReminderCreate(BaseModel):
    pet_id: int
    title: str  # e.g., "Give medication"
    description: Optional[str] = None
    reminder_type: ReminderType  # MEDICATION, FEEDING, WATER, CLEANING, CUSTOM
    frequency: Frequency  # DAILY, WEEKLY, MONTHLY, CUSTOM
    time: time  # HH:MM
    days_of_week: Optional[List[int]] = None  # array [0,1,2,3,4,5,6] where 0=Monday
    is_active: bool = True

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_type: Optional[ReminderType] = None
    frequency: Optional[Frequency] = None
    time: Optional[time] = None
    days_of_week: Optional[List[int]] = None
    is_active: Optional[bool] = None

class ReminderResponse(BaseModel):
    id: int
    pet_id: int
    title: str
    description: Optional[str]
    reminder_type: ReminderType
    frequency: Frequency
    time: time
    days_of_week: Optional[List[int]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ReminderLog Schemas
class ReminderLogCreate(BaseModel):
    reminder_id: int
    scheduled_at: datetime
    status: ReminderLogStatus  # PENDING, DONE, SKIPPED
    executed_at: Optional[datetime] = None  # Optional, can be set when status is DONE

class ReminderLogUpdate(BaseModel):
    status: Optional[ReminderLogStatus] = None
    executed_at: Optional[datetime] = None

class ReminderLogResponse(BaseModel):
    id: int
    reminder_id: int
    scheduled_at: datetime
    executed_at: Optional[datetime]
    status: ReminderLogStatus
    
    class Config:
        from_attributes = True

# Admin Schemas
class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    pets_count: int
    routines_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

class AdminStatsResponse(BaseModel):
    total_users: int
    total_pets: int
    total_active_routines: int
    routines_completed_today: int
    active_users_last_7_days: int

class SettingsResponse(BaseModel):
    key: str
    value: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class SettingsUpdate(BaseModel):
    value: str
