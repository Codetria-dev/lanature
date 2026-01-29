"""
Application-wide constants and enums.

This module centralizes all constants, status values, and role definitions
to ensure consistency across the application and make maintenance easier.
"""

from enum import Enum


# ============================================================================
# USER ROLES
# ============================================================================

class UserRole(str, Enum):
    """
    User role definitions.
    
    Roles are used to control access to different parts of the application:
    - USER: Standard user with access to their own pets and routines
    - ADMIN: Administrator with access to all users and system settings
    
    Decision: Using enum instead of simple boolean (is_superuser) provides
    flexibility for future role additions (e.g., MODERATOR, VET, etc.)
    without requiring database migrations.
    """
    USER = "USER"
    ADMIN = "ADMIN"


# ============================================================================
# STATUS CONSTANTS
# ============================================================================

class RoutineLogStatus(str, Enum):
    """
    Status values for routine log entries.
    
    These statuses track the completion state of routine tasks:
    - DONE: Task was completed successfully
    - SKIPPED: Task was intentionally skipped
    - PENDING: Task is pending (for future use with scheduled reminders)
    
    Decision: Using enum ensures type safety and prevents invalid status values
    from being stored in the database. String comparison is avoided in favor
    of enum comparison.
    """
    DONE = "done"
    SKIPPED = "skipped"
    PENDING = "pending"


class ReminderLogStatus(str, Enum):
    """
    Status values for reminder log entries.
    
    These statuses track the execution state of reminders:
    - PENDING: Reminder is scheduled but not yet executed
    - DONE: Reminder was executed successfully
    - SKIPPED: Reminder was intentionally skipped
    
    Decision: Separate enum from RoutineLogStatus because reminders have
    a different lifecycle (scheduled -> executed) compared to routine logs
    (task -> completed).
    """
    PENDING = "PENDING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"


class ActiveStatus(Enum):
    """
    Active/Inactive status for entities.
    
    Used for:
    - User accounts (is_active)
    - Routine tasks (active)
    - Reminders (is_active)
    
    Decision: Centralized constant prevents magic boolean values scattered
    throughout the codebase. Makes it easier to change default behavior
    and ensures consistency.
    
    Note: Values are booleans, not strings, since they're used with Boolean
    database columns. Use .value to get the boolean value.
    """
    ACTIVE = True
    INACTIVE = False


# ============================================================================
# ROUTINE TASK TYPES
# ============================================================================

class RoutineTaskType(str, Enum):
    """
    Common routine task types.
    
    These are suggested types, but the system allows custom types as well.
    Common types include:
    - FEEDING: Food/meal times
    - MEDICATION: Medication administration
    - WATER: Water refresh
    - CLEANING: Cleaning tasks (cage, litter box, etc.)
    - EXERCISE: Exercise or playtime
    - GROOMING: Grooming tasks
    
    Decision: Enum provides autocomplete and validation, but custom strings
    are still allowed to accommodate unique pet care needs.
    """
    FEEDING = "feeding"
    MEDICATION = "medication"
    WATER = "water"
    CLEANING = "cleaning"
    EXERCISE = "exercise"
    GROOMING = "grooming"
    CUSTOM = "custom"


# ============================================================================
# FREQUENCY TYPES
# ============================================================================

class FrequencyType(str, Enum):
    """
    Frequency options for routines and reminders.
    
    - DAILY: Every day
    - WEEKLY: Once per week
    - MONTHLY: Once per month
    - CUSTOM: Custom schedule (uses days_of_week array)
    
    Decision: Centralized enum ensures consistency between RoutineTask
    frequency strings and Reminder frequency enums.
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# ============================================================================
# REMINDER TYPES
# ============================================================================

# Note: ReminderType, Frequency, and ReminderLogStatus enums are defined
# in models.py for SQLAlchemy compatibility. They are re-exported here
# for application code convenience. Import from models if you need the enum class.
# For string values, use the constants below or import from models.


# ============================================================================
# DEFAULT VALUES
# ============================================================================

class Defaults:
    """
    Default values used throughout the application.
    
    Centralized defaults make it easy to change application-wide behavior
    without searching through multiple files.
    """
    # User defaults
    USER_ROLE = UserRole.USER
    USER_IS_ACTIVE = True
    
    # Routine defaults
    ROUTINE_TASK_ACTIVE = True
    
    # Reminder defaults
    REMINDER_IS_ACTIVE = True
    
    # Pagination (for future use)
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
