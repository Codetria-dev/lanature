"""
Authentication and authorization utilities.

This module handles user authentication (login/password) and authorization (roles).
Uses JWT tokens for stateless authentication and bcrypt for password hashing.

Architectural decisions:
- JWT tokens for scalability (no server-side session storage)
- bcrypt for password hashing (industry standard, slow by design)
- Role-based access control via is_superuser flag (maps to UserRole enum)
- Token expiration for security (default 30 minutes, configurable)
"""

from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.constants import UserRole
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
# Decision: Environment variables allow different configs for dev/staging/prod
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "your-secret-key-change-in-production":
    raise RuntimeError(
        "SECRET_KEY environment variable is required and must not use a default placeholder value."
    )
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for storage
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Extract and validate current user from JWT token.
    
    This dependency is used in protected routes to get the authenticated user.
    Token must be valid and user must exist and be active.
    
    Decision: Stateless authentication via JWT allows horizontal scaling without
    shared session storage. Token contains user email (sub claim).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


def require_admin_role(user: User) -> User:
    """
    Verify user has ADMIN role (is_superuser=True).
    
    Decision: Centralized role check function ensures consistent error messages
    and makes it easy to change role checking logic in the future.
    
    Returns: User if admin, raises HTTPException if not.
    """
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. {UserRole.ADMIN.value} role required."
        )
    return user


def require_user_role(user: User) -> User:
    """
    Verify user has USER role (standard user, not admin).
    
    Useful for endpoints that should be accessible only to regular users,
    not administrators (e.g., to prevent admins from accessing user features).
    """
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. {UserRole.USER.value} role required."
        )
    return user
