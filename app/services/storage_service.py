"""
Supabase storage service for file management
"""
import os
import uuid
from typing import Optional, Dict, Any, List
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage in Supabase"""

    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET

        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured")
            self.client: Optional[Client] = None
        else:
            self.client = create_client(self.supabase_url, self.supabase_key)

    def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        user_id: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """
        Upload a file to Supabase storage

        Args:
            file_path: Path where to store the file (e.g., "users/{user_id}/images/{filename}")
            file_data: Binary file data
            user_id: User ID for organization
            content_type: MIME type of the file

        Returns:
            Public URL of the uploaded file or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            # Generate unique filename
            filename = os.path.basename(file_path)
            unique_filename = f"{uuid.uuid4()}_{filename}"

            # Upload to Supabase storage
            result = self.client.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_data,
                file_options={
                    "content-type": content_type,
                    "upsert": False
                }
            )

            if result:
                # Get public URL
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_filename)
                logger.info(f"File uploaded successfully: {public_url}")
                return public_url

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")

        return None

    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Download a file from Supabase storage

        Args:
            file_path: Path to the file in storage

        Returns:
            File data as bytes or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            result = self.client.storage.from_(self.bucket_name).download(file_path)

            if result:
                logger.info(f"File downloaded successfully: {file_path}")
                return result

        except Exception as e:
            logger.error(f"Failed to download file: {e}")

        return None

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase storage

        Args:
            file_path: Path to the file in storage

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False

        try:
            result = self.client.storage.from_(self.bucket_name).remove([file_path])

            if result:
                logger.info(f"File deleted successfully: {file_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")

        return False

    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """
        List files in a folder

        Args:
            folder_path: Folder path to list files from

        Returns:
            List of file information dictionaries
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []

        try:
            result = self.client.storage.from_(self.bucket_name).list(
                path=folder_path,
                options={"limit": 100}
            )

            return result or []

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get public URL for a file

        Args:
            file_path: Path to the file in storage

        Returns:
            Public URL or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Failed to get file URL: {e}")
            return None

    def create_user_folder(self, user_id: str) -> bool:
        """
        Create a folder structure for a user

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        # Supabase storage doesn't require explicit folder creation
        # This is just a placeholder for future folder organization
        return True


# Global storage service instance
storage_service = StorageService()
