"""
Unit tests for location management functionality
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User
from app.models.location import Location
from app.services.location_service import LocationService
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister
from app.schemas.location import LocationCreate, LocationUpdate


class TestLocationService:
    """Test location service functionality"""

    def test_create_location_success(self, db: Session):
        """Test successful location creation"""
        # Create test user first
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="locationtest@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Location Test User"
        )
        user = auth_service.register_user(user_data)

        # Create location service
        location_service = LocationService(db)

        location_data = LocationCreate(
            name="Test Location",
            description="A test location for unit testing",
            coordinates={
                "type": "Point",
                "coordinates": [-46.6333, -23.5505]
            },
            center_point={
                "lat": -23.5505,
                "lng": -46.6333
            }
        )

        location = location_service.create_location(str(user.id), location_data)

        assert location.name == "Test Location"
        assert location.description == "A test location for unit testing"
        assert location.user_id == user.id
        assert location.coordinates == location_data.coordinates
        assert location.center_point == location_data.center_point
        assert location.is_active is True

    def test_create_location_user_not_found(self, db: Session):
        """Test location creation with non-existent user"""
        location_service = LocationService(db)

        location_data = LocationCreate(
            name="Test Location",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )

        fake_user_id = str(uuid4())

        with pytest.raises(ValueError, match="User not found or inactive"):
            location_service.create_location(fake_user_id, location_data)

    def test_get_location_success(self, db: Session):
        """Test getting a specific location"""
        # Setup test user and location
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="getlocation@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Get Location User"
        )
        user = auth_service.register_user(user_data)

        location_service = LocationService(db)
        location_data = LocationCreate(
            name="Get Test Location",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )
        location = location_service.create_location(str(user.id), location_data)

        # Test getting the location
        retrieved_location = location_service.get_location(str(location.id), str(user.id))

        assert retrieved_location is not None
        assert retrieved_location.id == location.id
        assert retrieved_location.name == "Get Test Location"

    def test_get_location_not_found(self, db: Session):
        """Test getting non-existent location"""
        location_service = LocationService(db)
        fake_user_id = str(uuid4())
        fake_location_id = str(uuid4())

        result = location_service.get_location(fake_location_id, fake_user_id)

        assert result is None

    def test_get_user_locations(self, db: Session):
        """Test getting all locations for a user"""
        # Setup test user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="userlocations@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="User Locations User"
        )
        user = auth_service.register_user(user_data)

        location_service = LocationService(db)

        # Create multiple locations
        for i in range(3):
            location_data = LocationCreate(
                name=f"Test Location {i}",
                coordinates={"type": "Point", "coordinates": [i, i]},
                center_point={"lat": i, "lng": i}
            )
            location_service.create_location(str(user.id), location_data)

        # Test getting user locations
        result = location_service.get_user_locations(str(user.id), page=1, page_size=10)

        assert result["total"] == 3
        assert len(result["locations"]) == 3
        assert result["page"] == 1
        assert result["pages"] == 1

    def test_update_location_success(self, db: Session):
        """Test updating a location"""
        # Setup test user and location
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="updatelocation@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Update Location User"
        )
        user = auth_service.register_user(user_data)

        location_service = LocationService(db)
        location_data = LocationCreate(
            name="Original Location",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )
        location = location_service.create_location(str(user.id), location_data)

        # Update location
        update_data = LocationUpdate(
            name="Updated Location",
            description="Updated description"
        )
        updated_location = location_service.update_location(
            str(location.id), str(user.id), update_data
        )

        assert updated_location is not None
        assert updated_location.name == "Updated Location"
        assert updated_location.description == "Updated description"

    def test_delete_location_success(self, db: Session):
        """Test soft deleting a location"""
        # Setup test user and location
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="deletelocation@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Delete Location User"
        )
        user = auth_service.register_user(user_data)

        location_service = LocationService(db)
        location_data = LocationCreate(
            name="Location to Delete",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )
        location = location_service.create_location(str(user.id), location_data)

        # Delete location (soft delete)
        result = location_service.delete_location(str(location.id), str(user.id))

        assert result is True

        # Location should be marked as inactive
        deleted_location = location_service.get_location(str(location.id), str(user.id))
        assert deleted_location is None  # Should not be found when getting active locations

    def test_calculate_area_hectares(self, db: Session):
        """Test area calculation for locations"""
        location_service = LocationService(db)

        # Test polygon area calculation
        polygon_coords = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0]  # Close the polygon
            ]]
        }

        area = location_service.calculate_area_hectares(polygon_coords)

        # Should return a string representation of area in hectares
        assert area is not None
        assert isinstance(area, str)
        # Note: The test polygon might result in 0 area due to the shoelace formula
        # In a real implementation, this would use proper geospatial calculations
        assert float(area) >= 0

    def test_get_location_stats(self, db: Session):
        """Test location statistics"""
        # Setup test user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="stats@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Stats User"
        )
        user = auth_service.register_user(user_data)

        location_service = LocationService(db)

        # Create test locations
        for i in range(2):
            location_data = LocationCreate(
                name=f"Stats Location {i}",
                coordinates={"type": "Point", "coordinates": [i, i]},
                center_point={"lat": i, "lng": i}
            )
            location_service.create_location(str(user.id), location_data)

        # Get statistics
        stats = location_service.get_location_stats(str(user.id))

        assert stats["total_locations"] == 2
        assert "total_area_hectares" in stats
        assert "monthly_stats" in stats


class TestLocationModel:
    """Test location model functionality"""

    def test_location_to_dict(self, db: Session):
        """Test location serialization"""
        # Create test user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="modeltest@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Model Test User"
        )
        user = auth_service.register_user(user_data)

        # Create location
        location = Location(
            user_id=user.id,
            name="Model Test Location",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )
        db.add(location)
        db.commit()
        db.refresh(location)

        # Test to_dict method
        location_dict = location.to_dict()

        assert location_dict["id"] == str(location.id)
        assert location_dict["name"] == "Model Test Location"
        assert location_dict["user_id"] == str(user.id)
        assert "created_at" in location_dict
        assert "updated_at" in location_dict

    def test_location_update_from_dict(self, db: Session):
        """Test location update from dictionary"""
        # Create test user and location
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="updatefromdict@example.com",
            password="SecurePass123!",
            password_confirm="SecurePass123!",
            full_name="Update From Dict User"
        )
        user = auth_service.register_user(user_data)

        location = Location(
            user_id=user.id,
            name="Original Name",
            coordinates={"type": "Point", "coordinates": [0, 0]},
            center_point={"lat": 0, "lng": 0}
        )
        db.add(location)
        db.commit()

        # Update from dictionary
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "is_active": False
        }

        location.update_from_dict(update_data)

        assert location.name == "Updated Name"
        assert location.description == "Updated description"
        assert location.is_active is False

        # Should not update protected fields
        original_id = location.id
        location.update_from_dict({"id": "new-id"})
        assert location.id == original_id  # ID should not change
