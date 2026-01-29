"""
Authentication router for user registration and login.

Handles user registration, login, and profile management.
All endpoints are public (no authentication required for register/login).

Architectural decisions:
- Registration automatically creates USER role (not ADMIN)
- Login validates user is active before allowing access
- JWT tokens contain user email for stateless authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate, Token, LoginRequest
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user as auth_get_current_user
)
from app.constants import UserRole, Defaults, ActiveStatus

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Decision: All new registrations are created with USER role (is_superuser=False)
    and active status (is_active=True). Only existing admins can create admin accounts.
    This prevents privilege escalation through registration.
    """
    # Check if email already exists
    db_user = get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with USER role (not ADMIN)
    # Decision: Default role is USER, active by default
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        is_superuser=False,  # UserRole.USER (mapped to is_superuser=False)
        is_active=Defaults.USER_IS_ACTIVE  # ActiveStatus.ACTIVE
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Decision: Inactive users cannot login, even with correct credentials
    # This allows admins to temporarily disable accounts without deletion
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(auth_get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    # Check if email is already in use by another user
    if user_update.email and user_update.email != current_user.email:
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    # Update provided fields
    if user_update.name is not None:
        current_user.name = user_update.name
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
