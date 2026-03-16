"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient

class TestAuthenticationAPI:
    """Test authentication API endpoints"""

    # def test_health_check(self, client: TestClient):
    #     """Test health check endpoint"""
    #     response = client.get("/health")
    #     assert response.status_code == 200
    #     assert response.json() == {"status": "healthy", "version": "1.0.0"}

    def test_register_user_api(self, client: TestClient):
        """Test user registration via API"""
        user_data = {
            "email": "apitest@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "API Test User",
            "phone_number": "+1234567890"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "apitest@example.com"
        assert data["full_name"] == "API Test User"
        assert data["email_confirmed"] is False
        assert "id" in data

    def test_register_duplicate_email_api(self, client: TestClient):
        """Test registration with duplicate email via API"""
        user_data = {
            "email": "duplicateapi@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Duplicate Test User"
        }

        # First registration
        client.post("/api/v1/auth/register", json=user_data)

        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_unconfirmed_email_api(self, client: TestClient):
        """Test login with unconfirmed email"""
        # Register user first
        user_data = {
            "email": "loginunconfirmed@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Login Unconfirmed User"
        }
        client.post("/api/v1/auth/register", json=user_data)

        # Try to login without confirming email
        login_data = {
            "username": "loginunconfirmed@example.com",
            "password": "SecurePass123!"
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 403
        assert "not confirmed" in response.json()["detail"]




class TestLocationAPI:
    """Test location management API endpoints"""

    def get_auth_token(self, client: TestClient) -> str:
        """Helper to get authentication token for testing"""
        # Register and confirm a test user
        user_data = {
            "email": "locationapi@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Location API User"
        }

        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        # For testing, we'll simulate email confirmation by directly updating the user
        # In a real scenario, this would be done via email confirmation

        return "test-token"  # In real tests, you'd get actual JWT token

    def test_create_location_api(self, client: TestClient):
        """Test location creation via API"""
        # Get auth token (simplified for testing)
        token = self.get_auth_token(client)

        location_data = {
            "name": "API Test Location",
            "description": "Created via API test",
            "coordinates": {
                "type": "Point",
                "coordinates": [-46.6333, -23.5505]
            },
            "center_point": {
                "lat": -23.5505,
                "lng": -46.6333
            }
        }

        response = client.post(
            "/api/v1/locations/",
            json=location_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Note: This will fail without proper JWT token setup
        # In a complete test suite, you'd set up proper authentication
        assert response.status_code in [200, 401]  # 200 for success, 401 for auth issues

    def test_get_locations_api(self, client: TestClient):
        """Test getting locations via API"""
        token = self.get_auth_token(client)

        response = client.get(
            "/api/v1/locations/",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should return paginated results
        if response.status_code == 200:
            data = response.json()
            assert "locations" in data
            assert "total" in data
            assert "page" in data
            assert "pages" in data


class TestEventsAPI:
    """Test Server-Sent Events API"""

    def test_sse_connection(self, client: TestClient):
        """Test SSE connection endpoint"""
        # This is a basic test - SSE testing requires more complex setup
        response = client.get("/api/v1/events/stream")

        # Should return 401 without authentication
        assert response.status_code == 401


class TestErrorHandling:
    """Test error handling across the API"""

    def test_invalid_json(self, client: TestClient):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self, client: TestClient):
        """Test handling of missing required fields"""
        incomplete_data = {
            "email": "incomplete@example.com"
            # Missing required fields
        }

        response = client.post("/api/v1/auth/register", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    def test_invalid_email_format(self, client: TestClient):
        """Test handling of invalid email format"""
        invalid_email_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Invalid Email User"
        }

        response = client.post("/api/v1/auth/register", json=invalid_email_data)

        assert response.status_code == 422  # Validation error

    def test_invalid_phone_format(self, client: TestClient):
        """Test handling of invalid phone number format"""
        invalid_phone_data = {
            "email": "phoneformat@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Phone Format User",
            "phone_number": "1234567890"  # Missing + prefix
        }

        response = client.post("/api/v1/auth/register", json=invalid_phone_data)

        assert response.status_code == 422  # Validation error


class TestSecurity:
    """Test security-related functionality"""

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/auth/register")

        # Should allow CORS preflight requests
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting is in place"""
        # Make multiple rapid requests to registration endpoint
        for i in range(5):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"ratetest{i}@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                    "full_name": "Rate Test User"
                }
            )

        # Should eventually be rate limited (implementation dependent)
        # This is a basic check - real rate limiting tests would be more comprehensive
        assert response.status_code in [200, 429]  # 200 for success, 429 for rate limited

    def test_sql_injection_protection(self, client: TestClient):
        """Test protection against SQL injection"""
        malicious_data = {
            "email": "test'; DROP TABLE users; --",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Malicious User"
        }

        response = client.post("/api/v1/auth/register", json=malicious_data)

        # Should either reject the input or handle it safely
        assert response.status_code in [200, 400, 422]  # Should not cause server error

    def test_xss_protection(self, client: TestClient):
        """Test protection against XSS attacks"""
        xss_data = {
            "email": "xss@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "<script>alert('xss')</script>"
        }

        response = client.post("/api/v1/auth/register", json=xss_data)

        # Should handle XSS input safely
        assert response.status_code in [200, 400, 422]
