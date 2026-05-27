from pydantic import BaseModel


class JobAcceptedResponse(BaseModel):
    job_id: str
    status: str = "queued"
    message: str
