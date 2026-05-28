from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.repositories.pipeline import PipelineRepository
from app.schemas.pipeline import PipelineMoveRequest, PipelineMoveResponse

router = APIRouter()


@router.post("/move", response_model=PipelineMoveResponse)
async def move_pipeline_stage(
    payload: PipelineMoveRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PipelineMoveResponse:
    result = await PipelineRepository(session).move_stage(
        lead_id=payload.lead_id,
        user_id=current_user.user_id,
        stage=payload.stage.value,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    await session.commit()
    return PipelineMoveResponse(**result)
