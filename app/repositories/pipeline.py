from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.pipeline import PipelineItem


class PipelineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def move_stage(self, lead_id: str, user_id: str, stage: str) -> dict:
        lead_result = await self.session.execute(
            select(Lead.id).where(Lead.id == lead_id, Lead.user_id == user_id)
        )
        if lead_result.scalar_one_or_none() is None:
            return {}

        item_result = await self.session.execute(
            select(PipelineItem).where(
                PipelineItem.lead_id == lead_id,
                PipelineItem.user_id == user_id,
            )
        )
        item = item_result.scalar_one_or_none()

        if item is None:
            item = PipelineItem(id=str(uuid4()), lead_id=lead_id, user_id=user_id, stage=stage)
            self.session.add(item)
        else:
            item.stage = stage

        await self.session.flush()
        return self.to_dict(item)

    @staticmethod
    def to_dict(item: PipelineItem) -> dict:
        return {
            "lead_id": item.lead_id,
            "stage": item.stage,
        }
