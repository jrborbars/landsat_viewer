"""
Location schemas for request/response validation
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
# UUID type removed for SQLite compatibility


class LocationBase(BaseModel):
    """Base schema for location data"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    coordinates: Dict[str, Any]  # GeoJSON format
    center_point: Dict[str, float]  # {lat: float, lng: float}
    bounds: Optional[Dict[str, Any]] = None
    area_hectares: Optional[str] = None

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate GeoJSON coordinates"""
        if not isinstance(v, dict):
            raise ValueError("Coordinates must be a GeoJSON object")

        if "type" not in v:
            raise ValueError("Coordinates must have a 'type' field")

        if v["type"] not in ["Point", "Polygon", "MultiPolygon"]:
            raise ValueError("Coordinates must be a Point, Polygon or MultiPolygon")

        if "coordinates" not in v:
            raise ValueError("Coordinates must have a 'coordinates' field")

        return v

    @field_validator("center_point")
    @classmethod
    def validate_center_point(cls, v):
        """Validate center point coordinates"""
        if not isinstance(v, dict):
            raise ValueError("Center point must be an object")

        if "lat" not in v or "lng" not in v:
            raise ValueError("Center point must have 'lat' and 'lng' fields")

        lat = v["lat"]
        lng = v["lng"]

        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")

        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")

        return v


class LocationCreate(LocationBase):
    """Schema for creating a new location"""
    pass


class LocationUpdate(BaseModel):
    """Schema for updating a location"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None
    center_point: Optional[Dict[str, float]] = None
    bounds: Optional[Dict[str, Any]] = None
    area_hectares: Optional[str] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    """Schema for location response"""
    id: str  # Changed from UUID to str for SQLite compatibility
    user_id: str  # Changed from UUID to str for SQLite compatibility
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationListResponse(BaseModel):
    """Schema for list of locations"""
    locations: List[LocationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class LocationWithImages(LocationResponse):
    """Schema for location with associated images"""
    images: List[Dict[str, Any]] = []


class LandsatImageRequest(BaseModel):
    """Schema for requesting Landsat images"""
    location_id: str  # Changed from UUID to str for SQLite compatibility
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD format
    bands: List[int] = Field(default=[5, 6, 7, 8])  # Default to NIR, SWIR-1, SWIR-2, PAN

    @field_validator("bands")
    @classmethod
    def validate_bands(cls, v):
        """Validate Landsat 8 band numbers"""
        valid_bands = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        for band in v:
            if band not in valid_bands:
                raise ValueError(f"Invalid band number: {band}. Must be one of {valid_bands}")
        return v


class ImageJobStatus(BaseModel):
    """Schema for image processing job status"""
    job_id: str
    status: str  # pending, downloading, processing, completed, failed
    progress: int  # 0-100
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ImageMetadata(BaseModel):
    """Schema for processed image metadata"""
    image_id: str  # Changed from UUID to str for SQLite compatibility
    location_id: str  # Changed from UUID to str for SQLite compatibility
    bands: List[int]
    date: str
    file_path: str
    file_size: int
    dimensions: Dict[str, int]  # width, height
    segmentation_method: str
    created_at: datetime
