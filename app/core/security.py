"""
Security utilities for password hashing and JWT token management
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import argon2
from jose import jwt

from app.core.config import settings


class PasswordSecurity:
    """Password security utilities using Argon2"""

    def __init__(self):
        self.ph = argon2.PasswordHasher(
            time_cost=settings.ARGON2_TIME_COST,
            memory_cost=settings.ARGON2_MEMORY_COST,
            parallelism=settings.ARGON2_PARALLELISM,
            hash_len=settings.ARGON2_HASH_LENGTH,
            salt_len=settings.ARGON2_SALT_LENGTH,
        )

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            self.ph.verify(hashed, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False

    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Check password strength based on OWASP/MIT guidelines
        Returns a dictionary with strength score and requirements met
        """
        score = 0
        requirements = {
            "length": len(password) >= 12,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "digits": any(c.isdigit() for c in password),
            "special_chars": any(not c.isalnum() for c in password),
            "not_common": password.lower() not in [
                "password", "123456", "password123", "admin", "qwerty"
            ],
        }

        # Calculate score based on requirements met
        score += 1 if requirements["length"] else 0
        score += 1 if requirements["uppercase"] else 0
        score += 1 if requirements["lowercase"] else 0
        score += 1 if requirements["digits"] else 0
        score += 1 if requirements["special_chars"] else 0
        score += 1 if requirements["not_common"] else 0

        strength_levels = {
            0: "very_weak",
            1: "weak",
            2: "fair",
            3: "good",
            4: "strong",
            5: "very_strong",
        }

        return {
            "score": score,
            "strength": strength_levels.get(score, "very_weak"),
            "requirements": requirements,
            "is_strong": score >= 4,
        }


class JWTManager:
    """JWT token management utilities"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"

    def create_access_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.JWTError:
            return None

    def get_token_subject(self, token: str) -> Optional[str]:
        """Extract subject from JWT token"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None


# Create global instances
password_security = PasswordSecurity()
jwt_manager = JWTManager()
