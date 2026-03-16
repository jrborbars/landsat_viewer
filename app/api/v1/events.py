"""
Server-Sent Events endpoints for real-time notifications
"""
from typing import Dict, Any
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import jwt_manager
from app.api.v1.auth import oauth2_scheme

from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Create a specialized OAuth2 scheme for SSE that doesn't auto-error
# This allows us to check the query parameter if the header is missing
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


class EventManager:
    """Manages Server-Sent Events connections and notifications"""

    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}
        self.user_connections: Dict[str, set] = {}

    async def connect(self, user_id: str) -> asyncio.Queue:
        """Create a new SSE connection for a user"""
        queue = asyncio.Queue()
        self.connections[user_id] = queue

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(queue)

        logger.info(f"User {user_id} connected to SSE")
        return queue

    def disconnect(self, user_id: str, queue: asyncio.Queue):
        """Remove an SSE connection"""
        if user_id in self.connections:
            del self.connections[user_id]

        if user_id in self.user_connections:
            self.user_connections[user_id].discard(queue)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"User {user_id} disconnected from SSE")

    async def send_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Send an event to a specific user"""
        if user_id in self.user_connections:
            event_data = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Send to all user's connections
            for queue in self.user_connections[user_id]:
                try:
                    await queue.put(event_data)
                except Exception as e:
                    logger.error(f"Failed to send event to user {user_id}: {e}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected users"""
        event_data = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected_users = []

        for user_id, queues in self.user_connections.items():
            for queue in queues:
                try:
                    await queue.put(event_data)
                except Exception as e:
                    logger.error(f"Failed to broadcast to user {user_id}: {e}")
                    if queue not in [q for qs in self.user_connections.values() for q in qs]:
                        disconnected_users.append((user_id, queue))

        # Clean up disconnected users
        for user_id, queue in disconnected_users:
            self.disconnect(user_id, queue)


# Global event manager instance
event_manager = EventManager()


def get_current_user_id(
    token: str = Depends(oauth2_scheme_optional),
    token_query: str = Query(None, alias="token")
) -> str:
    """Extract current user ID from JWT token (header or query param)"""
    auth_token = token or token_query
    
    if not auth_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    payload = jwt_manager.verify_token(auth_token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    return user_id


@router.get("/stream")
async def event_stream(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """SSE endpoint for real-time notifications"""

    async def event_generator():
        """Generate SSE events for the connected user"""
        queue = await event_manager.connect(user_id)

        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to notification stream'})}\n\n"

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for new events with timeout
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Format as SSE
                    yield f"data: {json.dumps(event_data)}\n\n"

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        except Exception as e:
            logger.error(f"SSE error for user {user_id}: {e}")
        finally:
            event_manager.disconnect(user_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/notify/{user_id}")
async def send_notification(
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Send a notification to a specific user (for internal use)"""
    await event_manager.send_to_user(user_id, event_type, data)
    return {"message": "Notification sent"}


@router.post("/broadcast")
async def broadcast_notification(
    event_type: str,
    data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Broadcast a notification to all connected users (for internal use)"""
    await event_manager.broadcast(event_type, data)
    return {"message": "Notification broadcasted"}


# Background task status notification helpers
async def notify_job_status(
    user_id: str,
    job_id: str,
    status: str,
    progress: int = 0,
    message: str = "",
    result: Dict[str, Any] = None,
    error: str = None,
):
    """Helper function to send job status notifications"""
    data = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message,
    }

    if result:
        data["result"] = result

    if error:
        data["error"] = error

    await event_manager.send_to_user(user_id, "job_status", data)


async def notify_location_created(user_id: str, location_data: Dict[str, Any]):
    """Helper function to notify about new location creation"""
    await event_manager.send_to_user(
        user_id,
        "location_created",
        {
            "location": location_data,
            "message": f"Location '{location_data.get('name')}' created successfully",
        }
    )


async def notify_image_processing_started(
    user_id: str,
    location_id: str,
    job_id: str,
    estimated_completion: str = None,
):
    """Helper function to notify about image processing start"""
    data = {
        "location_id": location_id,
        "job_id": job_id,
        "message": "Image processing started",
    }

    if estimated_completion:
        data["estimated_completion"] = estimated_completion

    await event_manager.send_to_user(user_id, "image_processing_started", data)


async def notify_image_processing_completed(
    user_id: str,
    location_id: str,
    job_id: str,
    result: Dict[str, Any],
):
    """Helper function to notify about image processing completion"""
    await event_manager.send_to_user(
        user_id,
        "image_processing_completed",
        {
            "location_id": location_id,
            "job_id": job_id,
            "result": result,
            "message": "Image processing completed successfully",
        }
    )
