from app.api.routes.jobs import format_job_error, normalize_job_status


def test_format_job_error_extracts_fastapi_detail_from_serialized_exception() -> None:
    error = "HTTPException(status_code=422, detail='Lead does not have a google_place_id to refresh')"

    assert format_job_error(error) == "Lead does not have a google_place_id to refresh"


def test_normalize_job_status_translates_celery_states_for_clients() -> None:
    assert normalize_job_status("PENDING") == "queued"
    assert normalize_job_status("STARTED") == "started"
    assert normalize_job_status("SUCCESS") == "completed"
    assert normalize_job_status("FAILURE") == "failed"
