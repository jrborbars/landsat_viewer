from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class ImageStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Image(BaseModel):
    """Model for satellite images associated with a location"""
    __tablename__ = "images"

    location_id = Column(String, ForeignKey("locations.id"), nullable=False, index=True)
    scene_id = Column(String, nullable=False, index=True)
    acquisition_date = Column(DateTime(timezone=True), nullable=False)
    
    # Status for Celery tracking (Blue/Green/Red logic)
    status = Column(String, default=ImageStatus.PENDING, nullable=False)
    
    # Geographic data
    bounds = Column(JSON, nullable=True)  # {minLat, maxLat, minLng, maxLng}
    
    # File storage info
    file_url = Column(String, nullable=True)
    processing_results = Column(JSON, nullable=True) # K-means data
    error_message = Column(String, nullable=True)

    # Relationships
    location = relationship("Location", back_populates="images")
