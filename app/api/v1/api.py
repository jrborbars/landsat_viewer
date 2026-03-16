"""
Main API router that includes all v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.locations import router as locations_router
from app.api.v1.events import router as events_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    locations_router,
    prefix="/locations",
    tags=["locations"]
)

api_router.include_router(
    events_router,
    prefix="/events",
    tags=["events"]
)
