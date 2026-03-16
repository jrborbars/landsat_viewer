"""
Core configuration settings for the Landsat Image Viewer application
"""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "Landsat Image Viewer"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A comprehensive Landsat satellite image viewer with processing capabilities"
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:80",     # Nginx
        "http://localhost:443",    # Nginx SSL
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse CORS origins from environment variable"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Password Security
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 102400
    ARGON2_PARALLELISM: int = 8
    ARGON2_HASH_LENGTH: int = 32
    ARGON2_SALT_LENGTH: int = 16

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/landsat_db"
    SQLITE_DATABASE_URL: str = "sqlite:///app/data/test.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-supabase-service-role-key"
    SUPABASE_STORAGE_BUCKET: str = "landsat-images"

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    # Email Configuration (Mailchimp)
    MAILCHIMP_API_KEY: str = "your-mailchimp-api-key"
    MAILCHIMP_FROM_EMAIL: str = "noreply@landsatviewer.com"
    MAILCHIMP_FROM_NAME: str = "Landsat Image Viewer"

    # Landsat API Configuration
    LANDSAT_API_USERNAME: str = "your-landsat-username"
    LANDSAT_API_PASSWORD: str = "your-landsat-password"

    # File Storage
    TEMP_DIR: str = "/app/temp"
    LOGS_DIR: str = "/app/logs"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # Nginx Configuration (for production)
    NGINX_PORT: int = 80
    NGINX_SSL_PORT: int = 443

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
