from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_from_place(self, payload: dict, user_id: str) -> dict:
        google_place_id = payload.get("google_place_id")
        lead = None

        if google_place_id:
            result = await self.session.execute(
                select(Lead).where(Lead.user_id == user_id, Lead.google_place_id == google_place_id)
            )
            lead = result.scalar_one_or_none()

        if lead is None:
            lead = Lead(id=str(uuid4()), user_id=user_id)
            self.session.add(lead)

        self.apply_place_payload(lead, payload)

        await self.session.flush()
        return self.to_dict(lead)

    async def update_from_place(self, lead_id: str, user_id: str, payload: dict) -> dict | None:
        result = await self.session.execute(
            select(Lead).where(Lead.id == lead_id, Lead.user_id == user_id)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            return None

        self.apply_place_payload(lead, payload)
        await self.session.flush()
        return self.to_dict(lead)

    async def get_by_id(self, lead_id: str, user_id: str) -> dict | None:
        result = await self.session.execute(
            select(Lead).where(Lead.id == lead_id, Lead.user_id == user_id)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            return None
        return self.to_dict(lead)


    async def list_competitors(
        self,
        lead: dict,
        user_id: str,
        limit: int = 20,
    ) -> list[dict]:
        filters = [Lead.user_id == user_id, Lead.id != lead["id"]]
        if lead.get("category"):
            filters.append(Lead.category == lead["category"])

        result = await self.session.execute(
            select(Lead)
            .where(*filters)
            .order_by(Lead.review_count.desc().nullslast(), Lead.rating.desc().nullslast())
            .limit(limit)
        )
        return [self.to_dict(item) for item in result.scalars().all()]

    async def list_by_user(self, user_id: str, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(Lead).where(Lead.user_id == user_id).order_by(Lead.created_at.desc()).limit(limit)
        )
        return [self.to_dict(lead) for lead in result.scalars().all()]

    @staticmethod
    def apply_place_payload(lead: Lead, payload: dict) -> None:
        lead.google_place_id = payload.get("google_place_id")
        lead.name = payload["name"]
        lead.address = payload.get("address")
        lead.phone = payload.get("phone")
        lead.website = payload.get("website")
        lead.rating = payload.get("rating")
        lead.review_count = payload.get("review_count")
        lead.category = payload.get("category")
        lead.latitude = payload.get("latitude")
        lead.longitude = payload.get("longitude")

    @staticmethod
    def to_dict(lead: Lead) -> dict:
        return {
            "id": lead.id,
            "google_place_id": lead.google_place_id,
            "name": lead.name,
            "address": lead.address,
            "phone": lead.phone,
            "website": lead.website,
            "rating": lead.rating,
            "review_count": lead.review_count,
            "category": lead.category,
            "latitude": lead.latitude,
            "longitude": lead.longitude,
        }
