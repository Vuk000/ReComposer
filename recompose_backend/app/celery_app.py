# --- Celery App Configuration ---
"""
Celery application configuration for background tasks.
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "recompose",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.email_tasks", "app.tasks.campaign_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    "process-pending-emails": {
        "task": "app.tasks.email_tasks.process_pending_emails",
        "schedule": 60.0,  # Every minute
    },
    "check-replies": {
        "task": "app.tasks.email_tasks.check_replies",
        "schedule": settings.REPLY_CHECK_INTERVAL_MINUTES * 60.0,  # Configurable interval
    },
}

