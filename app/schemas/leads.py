from typing import Any

from pydantic import BaseModel, Field


class LeadSearchRequest(BaseModel):
    niche: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=160)
    radius_meters: int = Field(default=8000, ge=100, le=50000)
    limit: int = Field(default=20, ge=1, le=60)


class LeadResponse(BaseModel):
    id: str
    google_place_id: str | None = None
    name: str
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class LeadSearchResultResponse(BaseModel):
    query: str
    location: str
    total: int
    leads: list[LeadResponse]


class LeadAnalysisResponse(BaseModel):
    id: str
    lead_id: str
    opportunity_score: float | None = None
    diagnosis: dict[str, Any]
