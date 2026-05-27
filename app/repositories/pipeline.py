from sqlalchemy.ext.asyncio import AsyncSession


class PipelineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def move_stage(self, lead_id: str, user_id: str, stage: str) -> dict:
        raise NotImplementedError
