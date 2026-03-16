"""
User model for authentication and user management
"""
from sqlalchemy import Column, String, Boolean, DateTime, func
import uuid_v7

from app.models.base import BaseModel


class User(BaseModel):
    """User model with authentication fields"""

    __tablename__ = "users"

    # Personal Information
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)  # ISO international format

    # Authentication
    hashed_password = Column(String, nullable=False)
    email_confirmed = Column(Boolean, default=False, nullable=False)
    email_confirmation_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    # Account Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Timestamps (inherited from BaseModel)
    # id, created_at, updated_at are inherited from BaseModel

    def __repr__(self) -> str:
        """String representation of user"""
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"

    def to_safe_dict(self) -> dict:
        """Return user data without sensitive information"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "email_confirmed": self.email_confirmed,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
