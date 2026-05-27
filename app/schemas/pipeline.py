from enum import StrEnum

from pydantic import BaseModel


class PipelineStage(StrEnum):
    new = "new"
    contacted = "contacted"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    closed = "closed"


class PipelineMoveRequest(BaseModel):
    lead_id: str
    stage: PipelineStage


class PipelineMoveResponse(BaseModel):
    lead_id: str
    stage: PipelineStage
