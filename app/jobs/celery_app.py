from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "busca_lead",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.jobs.lead_jobs", "app.jobs.analysis_jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
