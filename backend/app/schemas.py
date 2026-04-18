"""
Pydantic schemas for request/response validation.

This module defines all data transfer objects (DTOs) used in API endpoints.
Schemas provide automatic validation, serialization, and documentation.

Architectural decisions:
- Separate Create/Update/Response schemas for flexibility
- Using enums from constants for type safety
- Optional fields in Update schemas allow partial updates
"""

from pydantic import BaseModel, EmailStr, model_validator
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
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class LoginRequest(BaseModel):
    email: str  # Changed from EmailStr to allow "admin" as username
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
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
    type: Optional[str] = None
    task_type: Optional[str] = None
    frequency: str
    time: time
    active: Optional[bool] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def normalize_aliases(self):
        if self.type is None:
            self.type = self.task_type
        if self.active is None:
            self.active = self.is_active if self.is_active is not None else True
        if not self.type:
            raise ValueError("type/task_type is required")
        return self

class RoutineTaskUpdate(BaseModel):
    type: Optional[str] = None
    task_type: Optional[str] = None
    frequency: Optional[str] = None
    time: Optional[time] = None
    active: Optional[bool] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def normalize_aliases(self):
        if self.type is None and self.task_type is not None:
            self.type = self.task_type
        if self.active is None and self.is_active is not None:
            self.active = self.is_active
        return self

class RoutineTaskResponse(BaseModel):
    id: int
    routine_id: int
    pet_id: int  # Added for frontend convenience
    type: str
    task_type: str
    frequency: str
    time: time
    active: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# RoutineLog Schemas
class RoutineLogCreate(BaseModel):
    """Schema for creating routine log entries."""
    task_id: int
    date: date
    status: RoutineLogStatus

class RoutineLogResponse(BaseModel):
    """Schema for routine log responses."""
    id: int
    task_id: int
    date: date
    status: RoutineLogStatus
    
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


class SubscriptionPlanResponse(BaseModel):
    code: str
    name: str
    monthly_price_cents: int
    trial_days: int
    max_pets: int
    max_routines_per_pet: int
    is_active: bool

    class Config:
        from_attributes = True


class UserSubscriptionResponse(BaseModel):
    id: int
    status: str
    cancel_at_period_end: bool
    current_period_start: datetime
    current_period_end: datetime
    trial_ends_at: Optional[datetime]
    provider: Optional[str]
    provider_subscription_id: Optional[str]
    plan: SubscriptionPlanResponse

    class Config:
        from_attributes = True


class ChangePlanRequest(BaseModel):
    plan_code: str


class UsageResponse(BaseModel):
    pets_count: int
    tasks_count: int
    max_pets: int
    max_routines_per_pet: int

# Two-Factor Authentication (2FA) Schemas - Phase 2
class TwoFactorSetupResponse(BaseModel):
    """Response for 2FA setup initiation."""
    secret: str  # Base32-encoded TOTP secret
    qr_code: str  # Base64-encoded QR code image (data URI)
    backup_codes: List[str]  # 10 backup codes for recovery
    manual_entry_key: str  # Alternative to QR code for manual entry

class TwoFactorVerifyRequest(BaseModel):
    """Request to verify and confirm 2FA setup."""
    code: str  # 6-digit TOTP code

class TwoFactorDisableRequest(BaseModel):
    """Request to disable 2FA."""
    password: str  # Require password for security

class TwoFactorCodeRequest(BaseModel):
    """Request to verify TOTP/backup code during login."""
    code: str  # 6-digit TOTP code or backup code

class BackupCodesResponse(BaseModel):
    """Response with newly generated backup codes."""
    backup_codes: List[str]
    message: str = "New backup codes generated. Store them in a safe place."


# Refresh Token Schemas - Phase 2 Part 3
class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


class LogoutResponse(BaseModel):
    """Response for logout endpoint."""
    message: str = "Successfully logged out"


# Password Security Schemas - Phase 2 Part 4
class ChangePasswordRequest(BaseModel):
    """Request to change user password."""
    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    """Response for password change."""
    message: str = "Password changed successfully"


# GDPR Compliance Schemas - Phase 2 Part 5
class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: int
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime
    details: Optional[dict]

    class Config:
        from_attributes = True


class DataExportResponse(BaseModel):
    """Complete user data export for GDPR."""
    id: int
    name: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    is_2fa_enabled: bool
    pets: List[dict]  # Nested structure of pets, routines, tasks, logs
    audit_logs: List[AuditLogResponse]

    class Config:
        from_attributes = True


class DeleteAccountRequest(BaseModel):
    """Request to delete account."""
    password: str
    confirmation: str = "I want to delete my account"  # Safety confirmation string
