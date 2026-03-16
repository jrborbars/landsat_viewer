"""
Authentication endpoints for user management
"""
from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import jwt_manager
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailConfirmation,
    RefreshTokenRequest,
)
from app.services.auth_service import get_auth_service
from app.models.user import User
from app.core.security import password_security

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_data: UserRegister,
) -> Any:
    """Register a new user"""
    # Validate password strength
    strength = password_security.check_password_strength(user_data.password)
    if not strength["is_strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is not strong enough",
        )

    auth_service = get_auth_service(db)

    try:
        user = auth_service.register_user(user_data)
        return user.to_safe_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Login user and return JWT tokens"""
    auth_service = get_auth_service(db)

    # Convert form data to login schema
    login_data = UserLogin(email=form_data.username, password=form_data.password)

    try:
        user = auth_service.authenticate_user(login_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if email is confirmed
        if not user.email_confirmed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not confirmed. Please check your email for confirmation link.",
            )

        # Generate tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt_manager.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/confirm-email")
def confirm_email(
    *,
    db: Session = Depends(get_db),
    confirmation: EmailConfirmation,
) -> Any:
    """Confirm user email address"""
    auth_service = get_auth_service(db)

    if auth_service.confirm_email(confirmation.token):
        return {"message": "Email confirmed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token",
        )


@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest,
) -> Any:
    """Request password reset"""
    auth_service = get_auth_service(db)

    if auth_service.request_password_reset(reset_request.email):
        return {"message": "If the email exists, a password reset link has been sent"}
    else:
        # This should never happen, but just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request",
        )


@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(get_db),
    reset_confirm: PasswordResetConfirm,
) -> Any:
    """Reset user password"""
    auth_service = get_auth_service(db)

    if auth_service.reset_password(reset_confirm.token, reset_confirm.new_password):
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )


@router.post("/refresh", response_model=Dict[str, str])
def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_request: RefreshTokenRequest,
) -> Any:
    """Refresh access token"""
    auth_service = get_auth_service(db)

    new_access_token = auth_service.refresh_access_token(refresh_request.refresh_token)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {"access_token": new_access_token, "token_type": "bearer"}





@router.get("/me", response_model=UserResponse)
def get_current_user(
    *,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Any:
    """Get current user information"""
    payload = jwt_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Get user from database
    auth_service = get_auth_service(db)
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user.to_safe_dict()
