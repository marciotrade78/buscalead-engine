from app.jobs.celery_app import celery_app


@celery_app.task(name="lead.analyze")
def analyze_lead_job(lead_id: str, user_id: str) -> dict:
    raise NotImplementedError
