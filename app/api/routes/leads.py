from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.common import JobAcceptedResponse
from app.repositories.analyses import AnalysisRepository
from app.repositories.leads import LeadRepository
from app.schemas.leads import (
    LeadAnalysisResponse,
    LeadResponse,
    LeadSearchRequest,
    LeadSearchResultResponse,
)
from app.services.lead_search_service import LeadSearchService

router = APIRouter()


@router.post("/search", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def search_leads(
    payload: LeadSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> JobAcceptedResponse:
    return LeadSearchService().queue_search(payload=payload, current_user=current_user)


@router.post("/search/preview", response_model=LeadSearchResultResponse)
async def search_leads_preview(
    payload: LeadSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LeadSearchResultResponse:
    return await LeadSearchService().search_now(
        payload=payload,
        current_user=current_user,
        session=session,
        persist=False,
    )


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[LeadResponse]:
    return await LeadSearchService().list_leads(current_user=current_user, session=session)


@router.get("/{lead_id}/analysis", response_model=LeadAnalysisResponse)
async def get_latest_analysis(
    lead_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LeadAnalysisResponse:
    lead = await LeadRepository(session).get_by_id(lead_id, current_user.user_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    analysis = await AnalysisRepository(session).get_latest_for_lead(lead_id, current_user.user_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return LeadAnalysisResponse(**analysis)


@router.post("/{lead_id}/refresh", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def refresh_lead(
    lead_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> JobAcceptedResponse:
    return LeadSearchService().queue_refresh(lead_id=lead_id, current_user=current_user)


@router.post("/{lead_id}/analyze", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_lead(
    lead_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> JobAcceptedResponse:
    return LeadSearchService().queue_analysis(lead_id=lead_id, current_user=current_user)
