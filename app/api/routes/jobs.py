import re

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUser, get_current_user
from app.jobs.celery_app import celery_app
from app.schemas.jobs import JobStatusResponse

router = APIRouter()


def format_job_error(error: object) -> str | None:
    if error is None:
        return None

    detail = getattr(error, "detail", None)
    if detail:
        return str(detail)

    message = str(error)
    match = re.search(r"detail='([^']+)'", message)
    if match:
        return match.group(1)
    return message


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> JobStatusResponse:
    result = celery_app.AsyncResult(job_id)
    payload = result.result if result.successful() and isinstance(result.result, dict) else None
    error = format_job_error(result.result) if result.failed() else None
    return JobStatusResponse(
        job_id=job_id,
        status=result.status.lower(),
        result=payload,
        error=error,
    )
