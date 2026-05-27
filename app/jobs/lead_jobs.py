import asyncio

from app.auth.dependencies import CurrentUser
from app.db.session import AsyncSessionLocal
from app.jobs.celery_app import celery_app
from app.schemas.leads import LeadSearchRequest
from app.services.lead_search_service import LeadSearchService


@celery_app.task(name="lead.search")
def search_leads_job(payload: dict, user_id: str) -> dict:
    return asyncio.run(_search_leads(payload, user_id))


@celery_app.task(name="lead.refresh")
def refresh_lead_job(lead_id: str, user_id: str) -> dict:
    raise NotImplementedError


async def _search_leads(payload: dict, user_id: str) -> dict:
    async with AsyncSessionLocal() as session:
        typed_payload = LeadSearchRequest(**payload)
        current_user = CurrentUser(user_id=user_id)
        result = await LeadSearchService().search_now(typed_payload, current_user, session)
        return result.model_dump()
