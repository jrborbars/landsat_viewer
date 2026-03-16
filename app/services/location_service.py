"""
Location service for managing user-selected regions
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from uuid import UUID

from app.models.location import Location
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate
from app.core.config import settings


class LocationService:
    """Service for location management operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_location(self, user_id: UUID, location_data: LocationCreate) -> Location:
        """Create a new location for a user"""
        # Verify user exists and is active
        user = self.db.query(User).filter(
            User.id == str(user_id),
            User.is_active == True
        ).first()

        if not user:
            raise ValueError("User not found or inactive")

        # Create new location
        new_location = Location(
            user_id=str(user_id),
            **location_data.model_dump()
        )

        self.db.add(new_location)
        self.db.commit()
        self.db.refresh(new_location)

        # Send notification about location creation (simplified for testing)
        try:
            # For now, just log the notification (in production, this would send real-time updates)
            logger = logging.getLogger(__name__)
            logger.info(f"Location '{new_location.name}' created successfully for user {user_id}")
        except Exception as e:
            # Don't fail location creation if notification fails
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send location creation notification: {e}")

        return new_location

    def get_location(self, location_id: UUID, user_id: UUID) -> Optional[Location]:
        """Get a specific location by ID for a user"""
        location = self.db.query(Location).filter(
            and_(
                Location.id == str(location_id),
                Location.user_id == str(user_id),
                Location.is_active == True
            )
        ).first()

        return location

    def get_user_locations(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get all locations for a user with pagination"""
        # Build query
        query = self.db.query(Location).filter(Location.user_id == str(user_id))

        if not include_inactive:
            query = query.filter(Location.is_active == True)

        # Get total count
        total = query.count()

        # Apply pagination
        locations = query.order_by(desc(Location.created_at)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        # Calculate pagination info
        pages = (total + page_size - 1) // page_size

        return {
            "locations": locations,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    def update_location(
        self,
        location_id: UUID,
        user_id: UUID,
        location_data: LocationUpdate
    ) -> Optional[Location]:
        """Update a location"""
        location = self.get_location(location_id, user_id)

        if not location:
            return None

        # Update location fields
        update_data = location_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(location, key):
                setattr(location, key, value)

        self.db.commit()
        self.db.refresh(location)

        return location

    def delete_location(self, location_id: UUID, user_id: UUID) -> bool:
        """Soft delete a location (mark as inactive)"""
        location = self.get_location(location_id, user_id)

        if not location:
            return False

        location.is_active = False
        self.db.commit()

        return True

    def get_location_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get statistics about user's locations"""
        # Count total locations
        total_locations = self.db.query(Location).filter(
            and_(Location.user_id == user_id, Location.is_active == True)
        ).count()

        # Count locations by month (last 12 months)
        monthly_stats = []

        # Get total area (if available)
        total_area = self.db.query(Location.area_hectares).filter(
            and_(
                Location.user_id == user_id,
                Location.is_active == True,
                Location.area_hectares.isnot(None)
            )
        ).all()

        return {
            "total_locations": total_locations,
            "total_area_hectares": sum(float(area[0]) for area in total_area if area[0]),
            "monthly_stats": monthly_stats,
        }

    def calculate_area_hectares(self, coordinates: Dict[str, Any]) -> Optional[str]:
        """Calculate area in hectares from GeoJSON coordinates"""
        # This is a simplified area calculation
        # In a real implementation, you'd use a proper geospatial library
        try:
            if coordinates.get("type") == "Polygon":
                coords = coordinates["coordinates"][0]  # First ring of polygon

                # Simple area calculation using shoelace formula
                # This is approximate and doesn't account for projection
                if len(coords) < 3:
                    return None

                # Convert to approximate meters (simplified)
                area_m2 = 0
                n = len(coords) - 1

                for i in range(n):
                    j = (i + 1) % n
                    area_m2 += coords[i][0] * coords[j][1]
                    area_m2 -= coords[j][0] * coords[i][1]

                area_m2 = abs(area_m2) / 2

                # Convert to hectares (1 hectare = 10,000 m²)
                area_hectares = area_m2 / 10000

                return f"{area_hectares:.2f}"

        except (KeyError, IndexError, TypeError):
            pass

        return None


def get_location_service(db: Session) -> LocationService:
    """Dependency to get location service"""
    return LocationService(db)
