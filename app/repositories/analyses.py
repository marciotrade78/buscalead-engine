from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import LeadAnalysis


class AnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_diagnosis(self, lead_id: str, user_id: str, diagnosis: dict) -> dict:
        analysis = LeadAnalysis(
            id=str(uuid4()),
            lead_id=lead_id,
            user_id=user_id,
            opportunity_score=diagnosis.get("opportunity", {}).get("score"),
            diagnosis=diagnosis,
        )
        self.session.add(analysis)
        await self.session.flush()
        return self.to_dict(analysis)


    async def get_latest_for_lead(self, lead_id: str, user_id: str) -> dict | None:
        result = await self.session.execute(
            select(LeadAnalysis)
            .where(LeadAnalysis.lead_id == lead_id, LeadAnalysis.user_id == user_id)
            .order_by(LeadAnalysis.created_at.desc())
            .limit(1)
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            return None
        return self.to_dict(analysis)

    @staticmethod
    def to_dict(analysis: LeadAnalysis) -> dict:
        return {
            "id": analysis.id,
            "lead_id": analysis.lead_id,
            "opportunity_score": analysis.opportunity_score,
            "diagnosis": analysis.diagnosis,
        }
