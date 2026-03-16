"""
Location model for storing user-selected regions
"""
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, func, Text, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional

from app.models.base import BaseModel


class Location(BaseModel):
    """Location model for storing user-selected regions"""

    __tablename__ = "locations"

    # User relationship
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Location details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Geographic data
    coordinates = Column(JSON, nullable=False)  # GeoJSON format for polygon
    center_point = Column(JSON, nullable=False)  # {lat: float, lng: float}
    bounds = Column(JSON, nullable=True)  # Bounding box

    # Metadata
    area_hectares = Column(String(50), nullable=True)  # Calculated area
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", backref="locations")
    images = relationship("Image", back_populates="location", cascade="all, delete-orphan")

    # Timestamps (inherited from BaseModel)

    def __repr__(self) -> str:
        """String representation of location"""
        return f"<Location(id={self.id}, name={self.name}, user_id={self.user_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates,
            "center_point": self.center_point,
            "bounds": self.bounds,
            "area_hectares": self.area_hectares,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def update_from_dict(self, data: Dict[str, Any]) -> "Location":
        """Update location from dictionary"""
        updatable_fields = [
            "name", "description", "coordinates", "center_point",
            "bounds", "area_hectares", "is_active"
        ]

        for key, value in data.items():
            if key in updatable_fields and hasattr(self, key):
                setattr(self, key, value)
        return self
