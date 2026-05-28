import asyncio

from app.auth.dependencies import CurrentUser
from app.db.session import AsyncSessionLocal
from app.jobs.celery_app import celery_app
from app.services.analysis_service import AnalysisService


@celery_app.task(name="lead.analyze")
def analyze_lead_job(lead_id: str, user_id: str) -> dict:
    return asyncio.run(_analyze_lead(lead_id, user_id))


async def _analyze_lead(lead_id: str, user_id: str) -> dict:
    async with AsyncSessionLocal() as session:
        current_user = CurrentUser(user_id=user_id)
        return await AnalysisService().analyze_lead(lead_id, current_user, session)
