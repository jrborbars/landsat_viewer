"""
Celery tasks for Landsat image downloading and processing
"""
import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.image import Image, ImageStatus
from app.api.v1.events import event_manager

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def download_and_process_image(
    self,
    image_id: str,
    location_id: str,
    coordinates: Dict[str, Any],
    date: str,
    scene_id: str,
    entity_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Download and process a specific Landsat scene
    """
    db = SessionLocal()
    try:
        # Update database status
        image = db.query(Image).filter(Image.id == image_id).first()
        if image:
            image.status = ImageStatus.DOWNLOADING
            db.commit()

        # Notify frontend (Blue for processing/downloading)
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(event_manager.send_to_user(
            user_id, 
            "image_status_update", 
            {"image_id": image_id, "status": ImageStatus.DOWNLOADING, "message": f"Downloading scene {scene_id}"}
        ))

        # 1. Download
        # (Using existing logic from download_landsat_images but for a specific entity_id)
        # ... implementation details ...

        # 2. Process (K-means)
        # (Call the processing task logic here)
        
        # 3. Upload to Storage
        # (Upload resulting PNG/TIF to Supabase)

        # 4. Final Success Update (Green Checkmark)
        if image:
            image.status = ImageStatus.COMPLETED
            db.commit()
            
        loop.run_until_complete(event_manager.send_to_user(
            user_id, 
            "image_status_update", 
            {"image_id": image_id, "status": ImageStatus.COMPLETED, "message": "Success"}
        ))

        return {"status": "success", "image_id": image_id}

    except Exception as e:
        logger.error(f"Task failed for image {image_id}: {str(e)}")
        # Final Error Update (Red Alert)
        if image:
            image.status = ImageStatus.FAILED
            image.error_message = str(e)
            db.commit()
            
        loop.run_until_complete(event_manager.send_to_user(
            user_id, 
            "image_status_update", 
            {"image_id": image_id, "status": ImageStatus.FAILED, "error": str(e)}
        ))
        raise
    finally:
        db.close()



@celery_app.task
def cleanup_temp_files(temp_directory: str, older_than_hours: int = 24) -> bool:
    """
    Clean up temporary files older than specified hours

    Args:
        temp_directory: Directory to clean
        older_than_hours: Remove files older than this many hours

    Returns:
        Success status
    """
    try:
        if not os.path.exists(temp_directory):
            return True

        import time
        cutoff_time = time.time() - (older_than_hours * 3600)

        for filename in os.listdir(temp_directory):
            filepath = os.path.join(temp_directory, filename)
            if os.path.isfile(filepath):
                file_modified = os.path.getmtime(filepath)
                if file_modified < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Removed old temp file: {filepath}")

        # Remove empty directories
        if not os.listdir(temp_directory):
            shutil.rmtree(temp_directory)
            logger.info(f"Removed empty temp directory: {temp_directory}")

        return True

    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False
