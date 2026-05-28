from app.api.routes.jobs import format_job_error


def test_format_job_error_extracts_fastapi_detail_from_serialized_exception() -> None:
    error = "HTTPException(status_code=422, detail='Lead does not have a google_place_id to refresh')"

    assert format_job_error(error) == "Lead does not have a google_place_id to refresh"
