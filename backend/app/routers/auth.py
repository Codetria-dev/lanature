"""
Authentication router for user registration and login.

Handles user registration, login, and profile management.
All endpoints are public (no authentication required for register/login).

Architectural decisions:
- Registration automatically creates USER role (not ADMIN)
- Login validates user is active before allowing access
- JWT tokens contain user email for stateless authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, Token,
    TwoFactorSetupResponse, TwoFactorVerifyRequest, TwoFactorDisableRequest,
    TwoFactorCodeRequest, BackupCodesResponse, PasswordResetRequest,
    PasswordResetConfirm, EmailVerificationRequest, EmailVerificationConfirm,
    RefreshTokenRequest, LogoutResponse, ChangePasswordRequest, PasswordChangeResponse,
    DataExportResponse, DeleteAccountRequest, AuditLogResponse
)
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user_by_email,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user as auth_get_current_user
)
from app.constants import Defaults
from app.domain.settings_service import settings_service
from app.domain.two_factor_service import TwoFactorService
from app.domain.billing_service import billing_service
from app.domain.security_tokens_service import security_tokens_service
from app.domain.notification_service import notification_service
from app.domain.refresh_token_service import RefreshTokenService
from app.domain.password_security_service import PasswordSecurityService
from app.domain.gdpr_service import GDPRService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user.

    Decision: All new registrations are created with USER role (is_superuser=False)
    and active status (is_active=True). Only existing admins can create admin accounts.
    This prevents privilege escalation through registration.
    """
    settings_service.ensure_defaults(db)
    registration_enabled = settings_service.get_bool(db, "registration_enabled", True)
    if not registration_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )

    # Validate password strength
    is_valid, error_message = PasswordSecurityService.validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

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

    # Log registration to audit trail
    try:
        GDPRService.create_audit_log(
            db,
            action="registration",
            user_id=db_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        print(f"Audit log error: {e}")  # Fail gracefully

    # TODO: Implement billing and email verification
    # For now, skip these to allow registration to complete
    # billing_service.ensure_user_subscription(db, db_user.id, "pro")
    # verification_token = security_tokens_service.create_email_verification_token(db, db_user)
    # notification_service.send_email_verification(db_user.email, verification_token.token)

    return db_user

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")
    email = None
    password_value = None

    if "application/json" in content_type:
        payload = await request.json()
        email = payload.get("email") or payload.get("username")
        password_value = payload.get("password")
    else:
        form_data = await request.form()
        email = form_data.get("username") or form_data.get("email")
        password_value = form_data.get("password")

    if not email or not password_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email/username and password are required",
        )

    user = authenticate_user(db, email, password_value)
    if not user:
        # Log failed login attempt
        GDPRService.create_audit_log(
            db,
            action="login_failed",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"email": email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Decision: Inactive users cannot login, even with correct credentials
    # This allows admins to temporarily disable accounts without deletion
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    require_verified_email = settings_service.get_bool(db, "require_email_verification", False)
    if require_verified_email and not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = RefreshTokenService.create_refresh_token(db, user, expires_in_days=7)

    # Log successful login to audit trail
    GDPRService.create_audit_log(
        db,
        action="login_success",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

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


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(request: Request, payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if user:
        token_entry = security_tokens_service.create_password_reset_token(db, user)
        notification_service.send_password_reset_email(user.email, token_entry.token)
    return {"message": "If the email exists, reset instructions were sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: Request, payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    # Validate new password strength
    is_valid, error_message = PasswordSecurityService.validate_password(payload.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    user = security_tokens_service.consume_password_reset_token(db, payload.token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user.password_hash = get_password_hash(payload.new_password)
    db.commit()

    # Log password reset to audit trail
    GDPRService.create_audit_log(
        db,
        action="password_reset",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": "Password updated successfully"}


@router.post("/request-email-verification", status_code=status.HTTP_202_ACCEPTED)
def request_email_verification(
    request: Request,
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, payload.email)
    if user and not user.email_verified:
        token_entry = security_tokens_service.create_email_verification_token(db, user)
        notification_service.send_email_verification(user.email, token_entry.token)
    return {"message": "If the email exists, verification instructions were sent."}


@router.post("/verify-email", response_model=UserResponse)
def verify_email(request: Request, payload: EmailVerificationConfirm, db: Session = Depends(get_db)):
    user = security_tokens_service.consume_email_verification_token(db, payload.token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return user


# ============================================================================
# Two-Factor Authentication (2FA) Endpoints - Phase 2
# ============================================================================

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse, status_code=status.HTTP_200_OK)
def setup_2fa(
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate 2FA setup for the current user.

    Returns QR code and backup codes for authenticator app setup.
    2FA is not yet enabled until verified with a valid TOTP code.
    """
    if current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled for this account"
        )

    # Generate TOTP secret and QR code
    secret = TwoFactorService.generate_totp_secret(current_user.email)
    qr_code = TwoFactorService.generate_qr_code(secret, current_user.email)
    backup_codes = TwoFactorService.generate_backup_codes()
    manual_entry_key = TwoFactorService.get_totp_uri(secret, current_user.email)

    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "manual_entry_key": manual_entry_key
    }


@router.post("/2fa/verify", response_model=UserResponse, status_code=status.HTTP_200_OK)
def verify_2fa_setup(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify and confirm 2FA setup with a valid TOTP code.

    Requires a code from the authenticator app to confirm.
    """
    if current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled for this account"
        )

    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /2fa/setup first"
        )

    # Verify the TOTP code
    if not TwoFactorService.verify_totp(current_user.totp_secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired code"
        )

    # Enable 2FA for the user
    current_user.is_2fa_enabled = True
    current_user.backup_codes = TwoFactorService.generate_backup_codes()
    current_user.last_2fa_verification = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/2fa/disable", response_model=UserResponse, status_code=status.HTTP_200_OK)
def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for the current user.

    Requires password verification for security.
    """
    if not current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    # Verify password
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Disable 2FA
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    current_user.backup_codes = []
    current_user.last_2fa_verification = None
    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/2fa/backup-codes", response_model=BackupCodesResponse, status_code=status.HTTP_200_OK)
def generate_backup_codes(
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate new backup codes for the user.

    Replaces old backup codes with new ones.
    """
    if not current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    backup_codes = TwoFactorService.generate_backup_codes()
    current_user.backup_codes = backup_codes
    db.commit()

    return {
        "backup_codes": backup_codes,
        "message": "New backup codes generated. Store them in a safe place."
    }


@router.post("/2fa/verify-code", response_model=Token, status_code=status.HTTP_200_OK)
def verify_2fa_code(
    request: Request,
    verify_request: TwoFactorCodeRequest,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify a 2FA code (TOTP or backup) during login or other operations.

    Used after successful password verification if 2FA is enabled.
    """
    if not current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    code = verify_request.code.strip().replace("-", "").replace(" ", "")

    # Try TOTP code first
    if len(code) == 6 and code.isdigit():
        if TwoFactorService.verify_totp(current_user.totp_secret, code):
            current_user.last_2fa_verification = datetime.utcnow()
            db.commit()

            # Log successful 2FA verification
            GDPRService.create_audit_log(
                db,
                action="2fa_verification_success",
                user_id=current_user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

            # Create refresh token
            refresh_token = RefreshTokenService.create_refresh_token(db, current_user, expires_in_days=7)

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": current_user.email}, expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }

    # Try backup code
    is_valid, updated_codes = TwoFactorService.verify_backup_code(code, current_user.backup_codes)
    if is_valid:
        current_user.backup_codes = updated_codes
        current_user.last_2fa_verification = datetime.utcnow()
        db.commit()

        # Log successful 2FA verification with backup code
        GDPRService.create_audit_log(
            db,
            action="2fa_verification_success",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"method": "backup_code"}
        )

        # Create refresh token
        refresh_token = RefreshTokenService.create_refresh_token(db, current_user, expires_in_days=7)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.email}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # Invalid code - log failed attempt
    GDPRService.create_audit_log(
        db,
        action="2fa_verification_failed",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired code"
    )


# ============================================================================
# Refresh Token Endpoints - Phase 2 Part 3
# ============================================================================

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
def refresh_access_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Exchange a refresh token for a new access token and refresh token pair.

    Implements token rotation: old refresh token is invalidated, new one is issued.
    """
    # Validate refresh token format (should be a valid token string)
    if not refresh_request.refresh_token or len(refresh_request.refresh_token) < 20:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Hash the token to look it up
    token_hash = RefreshTokenService.hash_token(refresh_request.refresh_token)
    from app.models import RefreshToken
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get the user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found"
        )

    # Validate the token using the service
    if not RefreshTokenService.validate_refresh_token(db, user, refresh_request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Exchange for new token pair (old token is revoked)
    new_refresh_token = RefreshTokenService.refresh_token_pair(
        db, user, refresh_request.refresh_token
    )

    if new_refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout by revoking all refresh tokens for the current user.

    This invalidates all active sessions for the user.
    """
    # Revoke all tokens
    RefreshTokenService.revoke_user_tokens(db, current_user)

    # Log logout to audit trail
    GDPRService.create_audit_log(
        db,
        action="logout",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": "Successfully logged out"}


# ============================================================================
# Password Security Endpoints - Phase 2 Part 4
# ============================================================================

@router.post("/change-password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
def change_password(
    request: Request,
    password_request: ChangePasswordRequest,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the user's password.

    Requires verification of current password and validates new password strength.
    """
    # Verify current password
    if not verify_password(password_request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_message = PasswordSecurityService.validate_password(password_request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Check new password is different from current
    if verify_password(password_request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.password_hash = get_password_hash(password_request.new_password)
    db.commit()

    # Log password change to audit trail
    GDPRService.create_audit_log(
        db,
        action="password_changed",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    # Revoke all existing tokens (force re-login for security)
    RefreshTokenService.revoke_user_tokens(db, current_user)

    return {"message": "Password changed successfully"}


# ============================================================================
# GDPR Compliance Endpoints - Phase 2 Part 5
# ============================================================================

@router.get("/me/export", response_model=dict, status_code=status.HTTP_200_OK)
def export_user_data(
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR right to data portability).

    Returns a complete JSON export of all user data including profile, pets,
    routines, tasks, logs, and audit history.
    """
    # Log data export to audit trail
    GDPRService.create_audit_log(
        db,
        action="data_export",
        user_id=current_user.id,
        resource_type="user",
        resource_id=current_user.id,
        details={"format": "json"}
    )

    # Export user data
    exported_data = GDPRService.export_user_data(db, current_user)
    return exported_data


@router.delete("/me", response_model=dict, status_code=status.HTTP_200_OK)
def delete_account(
    request: Request,
    delete_request: DeleteAccountRequest,
    current_user: User = Depends(auth_get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data (GDPR right to be forgotten).

    Requires password verification and confirmation string for safety.
    This action is irreversible.
    """
    # Verify confirmation string
    if delete_request.confirmation != "I want to delete my account":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect confirmation string"
        )

    # Verify password
    if not verify_password(delete_request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    user_email = current_user.email
    user_id = current_user.id

    # Delete user (cascades to all related data)
    success = GDPRService.delete_user_data(db, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

    return {
        "message": "Account deleted successfully",
        "email": user_email
    }
