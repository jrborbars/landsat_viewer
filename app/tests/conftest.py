"""
Pytest configuration and fixtures for Landsat Image Viewer tests
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Set test environment
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["REDIS_URL"] = "redis://localhost:6379"

from app.core.config import settings
from app.core.database import Base, get_db, get_engine
from app.main import app

# Override the database URL for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Get the test engine
engine = get_engine()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

# Create all tables in the testing engine
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Database session fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """FastAPI test client fixture"""
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def async_client():
    """Async HTTP client fixture"""
    from fastapi.testclient import TestClient
    with TestClient(app, backend="asyncio") as ac:
        yield ac


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_database():
    """Set up database before each test and tear down after"""
    # Create all tables for in-memory database
    Base.metadata.create_all(bind=engine)
    yield
    # For in-memory database, no need to drop tables as they are temporary
