"""
Unit tests for authentication functionality
"""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import password_security


class TestAuthService:
    """Test authentication service"""

    def test_register_user_success(self, db: Session):
        """Test successful user registration"""
        auth_service = AuthService(db)

        user_data = UserRegister(
            email="test@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Test User",
            phone_number="+1234567890"
        )

        user = auth_service.register_user(user_data)

        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.phone_number == "+1234567890"
        assert user.email_confirmed is False
        assert user.hashed_password != "SecurePass123!"  # Should be hashed
        assert user.email_confirmation_token is not None

        # Verify password hashing
        assert password_security.verify_password("SecurePass123!", user.hashed_password)

    def test_register_user_duplicate_email(self, db: Session):
        """Test registration with duplicate email"""
        auth_service = AuthService(db)

        user_data = UserRegister(
            email="duplicate@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Test User"
        )

        # First registration
        auth_service.register_user(user_data)

        # Second registration with same email should fail
        with pytest.raises(ValueError, match="User with this email already exists"):
            auth_service.register_user(user_data)

    def test_authenticate_user_success(self, db: Session):
        """Test successful user authentication"""
        auth_service = AuthService(db)

        # Create test user
        user_data = UserRegister(
            email="auth@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Auth Test User"
        )
        user = auth_service.register_user(user_data)

        # Confirm email for login
        user.email_confirmed = True
        db.commit()

        # Test authentication
        login_data = UserLogin(email="auth@example.com", password="SecurePass123!")
        authenticated_user = auth_service.authenticate_user(login_data)

        assert authenticated_user is not None
        assert authenticated_user.email == "auth@example.com"
        assert authenticated_user.last_login is not None

    def test_authenticate_user_wrong_password(self, db: Session):
        """Test authentication with wrong password"""
        auth_service = AuthService(db)

        # Create test user
        user_data = UserRegister(
            email="wrongpass@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Wrong Pass User"
        )
        user = auth_service.register_user(user_data)
        user.email_confirmed = True
        db.commit()

        # Test with wrong password
        login_data = UserLogin(email="wrongpass@example.com", password="WrongPassword!")
        authenticated_user = auth_service.authenticate_user(login_data)

        assert authenticated_user is None

    def test_authenticate_user_unconfirmed_email(self, db: Session):
        """Test authentication with unconfirmed email"""
        auth_service = AuthService(db)

        # Create test user but don't confirm email
        user_data = UserRegister(
            email="unconfirmed@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Unconfirmed User"
        )
        user = auth_service.register_user(user_data)
        # email_confirmed remains False

        login_data = UserLogin(email="unconfirmed@example.com", password="SecurePass123!")

        # Should return user but last_login should be None (as email is not confirmed)
        authenticated_user = auth_service.authenticate_user(login_data)
        assert authenticated_user is not None
        assert authenticated_user.email == "unconfirmed@example.com"
        assert authenticated_user.last_login is None

    def test_confirm_email_success(self, db: Session):
        """Test email confirmation"""
        auth_service = AuthService(db)

        # Create test user
        user_data = UserRegister(
            email="confirm@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Confirm User"
        )
        user = auth_service.register_user(user_data)
        token = user.email_confirmation_token

        # Confirm email
        result = auth_service.confirm_email(token)

        assert result is True
        assert user.email_confirmed is True
        assert user.email_confirmation_token is None

    def test_confirm_email_invalid_token(self, db: Session):
        """Test email confirmation with invalid token"""
        auth_service = AuthService(db)

        result = auth_service.confirm_email("invalid-token")

        assert result is False

    def test_password_strength_check(self, db: Session):
        """Test password strength checking"""
        auth_service = AuthService(db)

        # Test weak password
        weak_result = auth_service.check_password_strength("123")
        assert weak_result["is_strong"] is False
        assert weak_result["score"] < 4

        # Test strong password
        strong_result = auth_service.check_password_strength("MySecurePass123!")
        assert strong_result["is_strong"] is True
        assert strong_result["score"] >= 4
        assert strong_result["requirements"]["length"] is True
        assert strong_result["requirements"]["uppercase"] is True
        assert strong_result["requirements"]["lowercase"] is True
        assert strong_result["requirements"]["digits"] is True
        assert strong_result["requirements"]["special_chars"] is True


class TestPasswordSecurity:
    """Test password security utilities"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "MySecurePassword123!"

        hashed = password_security.hash_password(password)
        assert hashed != password
        assert len(hashed) > 20  # Argon2 hash should be long

        # Verify password
        assert password_security.verify_password(password, hashed)

        # Test wrong password
        assert not password_security.verify_password("WrongPassword!", hashed)

    def test_password_strength_requirements(self):
        """Test password strength requirements"""
        # Test various password strengths
        test_cases = [
            ("weak", "123", False),
            ("fair", "password123", False),
            ("good", "MyPassword123", True),
            ("strong", "MySecurePass123!", True),
            ("very_strong", "MyVerySecurePassword123!@#", True),
        ]

        for strength_name, password, expected_strong in test_cases:
            result = password_security.check_password_strength(password)
            assert result["is_strong"] == expected_strong
            # Check that not_common is a boolean, not a list
            assert isinstance(result["requirements"]["not_common"], bool)
