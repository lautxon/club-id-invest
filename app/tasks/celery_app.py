"""
Celery Configuration and Tasks
Scheduled jobs for Club ID Invest platform.
"""

from celery import Celery
from datetime import timedelta
import logging

from app.core.config import get_settings

settings = get_settings()

# Configure Celery
celery_app = Celery(
    "club_id_invest",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.scheduled_tasks"],
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
    worker_max_tasks_per_child=100,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "check-auto-investment-trigger-daily": {
        "task": "app.tasks.scheduled_tasks.run_auto_investment_check",
        "schedule": timedelta(days=1),  # Run daily at midnight UTC
        "options": {"expires": 3600},  # Expire if not run within 1 hour
    },
    "manage-membership-lifecycle-daily": {
        "task": "app.tasks.scheduled_tasks.run_membership_lifecycle_check",
        "schedule": timedelta(days=1),  # Run daily at 1 AM UTC
        "options": {"expires": 3600},
    },
    "send-pending-contract-reminders": {
        "task": "app.tasks.scheduled_tasks.send_contract_reminders",
        "schedule": timedelta(hours=6),  # Run every 6 hours
        "options": {"expires": 1800},
    },
    "update-project-funding-progress": {
        "task": "app.tasks.scheduled_tasks.update_funding_progress",
        "schedule": timedelta(hours=1),  # Run hourly
        "options": {"expires": 900},
    },
}

logger = logging.getLogger(__name__)


def get_celery_app():
    """Get Celery application instance."""
    return celery_app
