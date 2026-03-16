"""
Celery application configuration for background tasks
"""
from celery import Celery
from app.core.config import settings

# Create Celery app instance
celery_app = Celery(
    "landsat_viewer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.landsat_tasks", "app.tasks.image_processing"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_routes={
        "app.tasks.landsat_tasks.*": {"queue": "landsat_download"},
        "app.tasks.image_processing.*": {"queue": "image_processing"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# Configure worker settings
celery_app.conf.update(
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

if __name__ == "__main__":
    celery_app.start()
