"""
Database configuration and session management
"""
import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Global engine variable
engine = None

def get_engine():
    """Get or create the SQLAlchemy engine"""
    global engine
    if engine is None:
        # Use environment variable if set, otherwise use settings
        database_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)

        # Use SQLite if the URL starts with sqlite
        if database_url.startswith('sqlite'):
            # SQLite configuration
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
            )
            
            # Set pragmas for better SQLite performance and reliability in Docker
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()
        else:
            # PostgreSQL configuration
            engine = create_engine(
                database_url,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_pre_ping=True,
                echo=settings.DEBUG,
            )
    return engine

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create base class for models
Base = declarative_base()
