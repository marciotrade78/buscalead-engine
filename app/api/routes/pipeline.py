from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUser, get_current_user
from app.schemas.pipeline import PipelineMoveRequest, PipelineMoveResponse

router = APIRouter()


@router.post("/move", response_model=PipelineMoveResponse)
async def move_pipeline_stage(
    payload: PipelineMoveRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> PipelineMoveResponse:
    return PipelineMoveResponse(lead_id=payload.lead_id, stage=payload.stage)
