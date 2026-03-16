"""
Base model with UUIDv7 support
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, func, String
from sqlalchemy.ext.declarative import declared_attr
import uuid_v7

from app.core.database import Base


def generate_uuid7() -> str:
    """Generate a UUIDv7 as string"""
    try:
        # Try the correct uuid_v7 usage
        return str(uuid_v7.uuid7())
    except AttributeError:
        # Fallback to standard UUID
        import uuid
        return str(uuid.uuid4())


class BaseModel(Base):
    """Base model with common fields"""

    __abstract__ = True

    # Generate UUIDv7 for ID (String type for SQLite compatibility)
    id = Column(
        String,
        primary_key=True,
        default=generate_uuid7,
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower() + "s"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update_from_dict(self, data: dict) -> "BaseModel":
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        return self
