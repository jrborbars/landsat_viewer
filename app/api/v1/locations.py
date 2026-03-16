"""
Location management endpoints
"""
from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import jwt_manager
from app.api.v1.auth import oauth2_scheme
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
    LandsatImageRequest,
)
from app.services.location_service import get_location_service
from app.models.image import Image, ImageStatus
from app.tasks.landsat_tasks import download_and_process_image

router = APIRouter()


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    """Extract current user ID from JWT token"""
    payload = jwt_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return UUID(user_id)


@router.post("/", response_model=LocationResponse)
def create_location(
    *,
    db: Session = Depends(get_db),
    location_data: LocationCreate,
    current_user_id: UUID = Depends(get_current_user_id),
) -> Any:
    """Create a new location"""
    location_service = get_location_service(db)

    try:
        location = location_service.create_location(current_user_id, location_data)

        # Calculate area if not provided
        if not location.area_hectares and location.coordinates:
            calculated_area = location_service.calculate_area_hectares(location.coordinates)
            if calculated_area:
                location.area_hectares = calculated_area
                db.commit()

        return location.to_dict()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=LocationListResponse)
def get_user_locations(
    *,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    include_inactive: bool = False,
) -> Any:
    """Get all locations for current user"""
    location_service = get_location_service(db)

    result = location_service.get_user_locations(
        current_user_id, page, page_size, include_inactive
    )

    return LocationListResponse(
        locations=[location.to_dict() for location in result["locations"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    *,
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> Any:
    """Get a specific location"""
    location_service = get_location_service(db)

    location = location_service.get_location(location_id, current_user_id)

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return location.to_dict()


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    *,
    location_id: UUID,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> Any:
    """Update a location"""
    location_service = get_location_service(db)

    location = location_service.update_location(location_id, current_user_id, location_data)

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return location.to_dict()


@router.delete("/{location_id}")
def delete_location(
    *,
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> Any:
    """Delete a location (soft delete)"""
    location_service = get_location_service(db)

    if location_service.delete_location(location_id, current_user_id):
        return {"message": "Location deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )


@router.get("/stats/summary")
def get_location_stats(
    *,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> Dict[str, Any]:
    """Get location statistics for current user"""
    location_service = get_location_service(db)

    return location_service.get_location_stats(current_user_id)


@router.post("/{location_id}/request-images")
def request_landsat_images(
    *,
    location_id: UUID,
    image_request: LandsatImageRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
) -> Any:
    """Request Landsat images for a location"""
    # 1. Verify location exists and belongs to user
    location_service = get_location_service(db)
    location = location_service.get_location(location_id, current_user_id)

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    # 2. Calculate Coverage (Scene Discovery)
    # For now, we search for scenes matching the date and location coordinates
    # In a full implementation, this would use a WRS-2 grid lookup
    from landsatxplore.api import API
    api = API(settings.LANDSAT_API_USERNAME, settings.LANDSAT_API_PASSWORD)
    
    scenes = api.search(
        dataset='landsat_ot_c2_l2',
        latitude=location.center_point['lat'],
        longitude=location.center_point['lng'],
        start_date=image_request.date,
        end_date=image_request.date,
        max_cloud_cover=20
    )
    api.logout()

    if not scenes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Landsat scenes found for date {image_request.date}",
        )

    # 3. Create Image records and trigger tasks
    jobs = []
    for scene in scenes:
        # Check if already exists
        existing = db.query(Image).filter(
            Image.location_id == str(location_id),
            Image.scene_id == scene['display_id']
        ).first()
        
        if existing:
            continue

        new_image = Image(
            location_id=str(location_id),
            scene_id=scene['display_id'],
            acquisition_date=datetime.fromisoformat(scene['acquisition_date'].replace('Z', '+00:00')),
            status=ImageStatus.PENDING,
            bounds={
                "minLat": scene['lower_left_latitude'],
                "maxLat": scene['upper_right_latitude'],
                "minLng": scene['lower_left_longitude'],
                "maxLng": scene['upper_right_longitude']
            }
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        # Trigger Celery Task
        task = download_and_process_image.delay(
            image_id=new_image.id,
            location_id=str(location_id),
            coordinates=location.coordinates,
            date=image_request.date,
            scene_id=scene['display_id'],
            entity_id=scene['entity_id'],
            user_id=str(current_user_id)
        )
        jobs.append({"image_id": new_image.id, "job_id": task.id})

    return {
        "message": f"Successfully queued {len(jobs)} image(s) for processing",
        "jobs": jobs
    }
