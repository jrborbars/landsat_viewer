"""
Authentication service for user management
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import password_security, jwt_manager
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserRegister) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Generate email confirmation token
        confirmation_token = self._generate_confirmation_token()

        # Create new user
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            hashed_password=password_security.hash_password(user_data.password),
            email_confirmation_token=confirmation_token,
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            # Send confirmation email (implement email service)
            # self._send_confirmation_email(new_user.email, confirmation_token)

            return new_user

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to create user")

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == login_data.email).first()

        if not user:
            return None

        if not user.is_active:
            raise ValueError("User account is disabled")

        if not password_security.verify_password(login_data.password, user.hashed_password):
            return None

        # Update last login only if email is confirmed
        if user.email_confirmed:
            user.last_login = datetime.utcnow()
            self.db.commit()

        return user

    def confirm_email(self, token: str) -> bool:
        """Confirm user email with token"""
        user = self.db.query(User).filter(
            User.email_confirmation_token == token
        ).first()

        if not user:
            return False

        user.email_confirmed = True
        user.email_confirmation_token = None
        self.db.commit()

        return True

    def request_password_reset(self, email: str) -> bool:
        """Request password reset for user"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if email exists or not for security
            return True

        # Generate reset token (expires in 1 hour)
        reset_token = self._generate_reset_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)

        self.db.commit()

        # Send reset email (implement email service)
        # self._send_password_reset_email(user.email, reset_token)

        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token"""
        user = self.db.query(User).filter(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow()
        ).first()

        if not user:
            return False

        # Update password and clear reset token
        user.hashed_password = password_security.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.last_login = datetime.utcnow()  # Force re-login

        self.db.commit()

        return True

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = jwt_manager.verify_token(refresh_token)

        if not payload:
            return None

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Verify user still exists and is active
        user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            return None

        # Generate new access token
        new_access_token = jwt_manager.create_access_token(subject=user_id)
        return new_access_token

    def check_password_strength(self, password: str) -> dict:
        """Check password strength"""
        return password_security.check_password_strength(password)

    def _generate_confirmation_token(self) -> str:
        """Generate email confirmation token"""
        return secrets.token_urlsafe(32)

    def _generate_reset_token(self) -> str:
        """Generate password reset token"""
        return secrets.token_urlsafe(32)

    def _send_confirmation_email(self, email: str, token: str):
        """Send email confirmation (implement with Mailchimp)"""
        # TODO: Implement Mailchimp email sending
        print(f"Sending confirmation email to {email} with token {token}")

    def _send_password_reset_email(self, email: str, token: str):
        """Send password reset email (implement with Mailchimp)"""
        # TODO: Implement Mailchimp email sending
        print(f"Sending password reset email to {email} with token {token}")


def get_auth_service(db: Session) -> AuthService:
    """Dependency to get auth service"""
    return AuthService(db)
