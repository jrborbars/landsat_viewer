"""
Authentication schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
# UUID type removed for SQLite compatibility


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = None

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format (basic validation)"""
        if v is None:
            return v
        # Basic phone number validation - should start with + and contain digits
        if not v.startswith("+"):
            raise ValueError("Phone number must be in international format (start with +)")
        # Remove + and check if remaining are digits
        digits_only = v[1:]
        if not digits_only.isdigit():
            raise ValueError("Phone number must contain only digits after +")
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 10-15 digits")
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response data"""
    id: str  # Changed from UUID to str for SQLite compatibility
    email: EmailStr
    full_name: str
    phone_number: Optional[str]
    email_confirmed: bool
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration


class TokenData(BaseModel):
    """Schema for token payload data"""
    sub: Optional[str] = None
    type: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match"""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailConfirmation(BaseModel):
    """Schema for email confirmation"""
    token: str


class PasswordStrengthResponse(BaseModel):
    """Schema for password strength check response"""
    score: int
    strength: str
    requirements: dict
    is_strong: bool


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str
