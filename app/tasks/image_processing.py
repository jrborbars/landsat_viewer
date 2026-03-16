"""
Celery tasks for image processing and segmentation
"""
import os
import tempfile
import shutil
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime
import rasterio
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import cv2

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_landsat_images(
    self,
    download_result: Dict[str, Any],
    n_clusters: int = 5,
    output_format: str = "GTiff"
) -> Dict[str, Any]:
    """
    Process downloaded Landsat images with K-means clustering segmentation

    Args:
        download_result: Result from download_landsat_images task
        n_clusters: Number of clusters for K-means (default: 5)
        output_format: Output image format (default: GTiff)

    Returns:
        Dictionary with processing results and output file paths
    """
    try:
        location_id = download_result["location_id"]
        downloaded_files = download_result["downloaded_files"]
        temp_dir = download_result["temp_directory"]

        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "message": "Starting image processing"}
        )

        if not downloaded_files:
            raise ValueError("No downloaded files to process")

        # Create output directory
        output_dir = os.path.join(temp_dir, "processed")
        os.makedirs(output_dir, exist_ok=True)

        processed_files = []
        total_files = len(downloaded_files)

        for i, file_info in enumerate(downloaded_files):
            try:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "progress": 10 + (i / total_files) * 60,
                        "message": f"Processing band {file_info['band']}"
                    }
                )

                # Process individual band
                processed_file = self._process_single_band(
                    file_info["file_path"],
                    output_dir,
                    n_clusters,
                    output_format
                )

                if processed_file:
                    processed_files.append(processed_file)

            except Exception as e:
                logger.error(f"Failed to process band {file_info['band']}: {str(e)}")
                continue

        if not processed_files:
            raise ValueError("No files were successfully processed")

        # Create composite image if multiple bands
        if len(processed_files) > 1:
            self.update_state(
                state="PROGRESS",
                meta={"progress": 80, "message": "Creating composite image"}
            )

            composite_file = self._create_composite_image(
                processed_files, output_dir, output_format
            )
        else:
            composite_file = processed_files[0] if processed_files else None

        self.update_state(
            state="PROGRESS",
            meta={"progress": 90, "message": "Processing completed"}
        )

        # Calculate total output size
        total_output_size = sum(
            os.path.getsize(f["file_path"]) for f in processed_files
        )

        return {
            "location_id": location_id,
            "scene_id": download_result["scene_id"],
            "processed_files": processed_files,
            "composite_file": composite_file,
            "processing_info": {
                "n_clusters": n_clusters,
                "output_format": output_format,
                "total_files": len(processed_files),
                "total_size": total_output_size,
            },
            "temp_directory": temp_dir,
            "output_directory": output_dir,
        }

    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise


def _process_single_band(
    input_path: str,
    output_dir: str,
    n_clusters: int,
    output_format: str
) -> Optional[Dict[str, Any]]:
    """
    Process a single Landsat band with K-means clustering

    Args:
        input_path: Path to input image file
        output_dir: Directory for output files
        n_clusters: Number of clusters for K-means
        output_format: Output format

    Returns:
        Dictionary with processed file information or None if failed
    """
    try:
        # Read image with rasterio
        with rasterio.open(input_path) as src:
            # Read image data
            image_data = src.read(1).astype(np.float32)

            # Reshape for clustering (flatten 2D array to 1D)
            pixels = image_data.reshape(-1, 1)

            # Remove nodata values
            valid_pixels = pixels[pixels != src.nodata] if src.nodata else pixels

            if len(valid_pixels) == 0:
                logger.warning(f"No valid pixels in {input_path}")
                return None

            # Normalize data
            scaler = StandardScaler()
            normalized_pixels = scaler.fit_transform(valid_pixels)

            # Apply K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(normalized_pixels)

            # Create segmented image
            segmented = np.zeros_like(pixels, dtype=np.uint8)
            segmented[pixels != src.nodata] = clusters + 1  # Start from 1

            # Reshape back to 2D
            segmented_2d = segmented.reshape(image_data.shape)

            # Create output filename
            filename = os.path.basename(input_path)
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_segmented.TIF"
            output_path = os.path.join(output_dir, output_filename)

            # Write segmented image
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=segmented_2d.shape[0],
                width=segmented_2d.shape[1],
                count=1,
                dtype=np.uint8,
                crs=src.crs,
                transform=src.transform,
            ) as dst:
                dst.write(segmented_2d, 1)

            return {
                "band": int(filename.split('_B')[1].split('.')[0]) if '_B' in filename else 0,
                "file_path": output_path,
                "file_size": os.path.getsize(output_path),
                "dimensions": {
                    "width": segmented_2d.shape[1],
                    "height": segmented_2d.shape[0]
                },
                "n_clusters": n_clusters,
            }

    except Exception as e:
        logger.error(f"Failed to process band {input_path}: {str(e)}")
        return None


def _create_composite_image(
    processed_files: List[Dict[str, Any]],
    output_dir: str,
    output_format: str
) -> Optional[Dict[str, Any]]:
    """
    Create a composite RGB image from processed bands

    Args:
        processed_files: List of processed band files
        output_dir: Output directory
        output_format: Output format

    Returns:
        Dictionary with composite file information or None if failed
    """
    try:
        # Sort files by band number
        sorted_files = sorted(processed_files, key=lambda x: x["band"])

        if len(sorted_files) < 3:
            logger.warning("Need at least 3 bands for RGB composite")
            return None

        # Use first 3 bands for RGB
        rgb_files = sorted_files[:3]

        # Read images
        images = []
        for file_info in rgb_files:
            with rasterio.open(file_info["file_path"]) as src:
                image = src.read(1)
                images.append(image)

        # Create RGB composite
        rgb_array = np.dstack(images)

        # Normalize to 0-255 range
        rgb_normalized = ((rgb_array - rgb_array.min()) * (255 / (rgb_array.max() - rgb_array.min()))).astype(np.uint8)

        # Create output filename
        composite_filename = "composite_rgb.TIF"
        composite_path = os.path.join(output_dir, composite_filename)

        # Write composite image
        with rasterio.open(rgb_files[0]["file_path"]) as src:
            with rasterio.open(
                composite_path,
                'w',
                driver='GTiff',
                height=rgb_normalized.shape[0],
                width=rgb_normalized.shape[1],
                count=3,
                dtype=np.uint8,
                crs=src.crs,
                transform=src.transform,
            ) as dst:
                for i in range(3):
                    dst.write(rgb_normalized[:, :, i], i + 1)

        return {
            "file_path": composite_path,
            "file_size": os.path.getsize(composite_path),
            "dimensions": {
                "width": rgb_normalized.shape[1],
                "height": rgb_normalized.shape[0]
            },
            "bands_used": [f["band"] for f in rgb_files],
        }

    except Exception as e:
        logger.error(f"Failed to create composite image: {str(e)}")
        return None


@celery_app.task
def upload_to_supabase(
    processed_result: Dict[str, Any],
    supabase_url: str = None,
    supabase_key: str = None,
    bucket_name: str = None,
) -> Dict[str, Any]:
    """
    Upload processed images to Supabase storage

    Args:
        processed_result: Result from process_landsat_images task
        supabase_url: Supabase project URL
        supabase_key: Supabase service role key
        bucket_name: Storage bucket name

    Returns:
        Dictionary with upload results
    """
    try:
        # TODO: Implement Supabase upload
        # This would use the Supabase Python client to upload files

        return {
            "uploaded_files": [],
            "total_uploaded": 0,
            "bucket": bucket_name,
        }

    except Exception as e:
        logger.error(f"Supabase upload failed: {str(e)}")
        raise
