from sqlalchemy.ext.asyncio import AsyncSession


class AnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_diagnosis(self, lead_id: str, diagnosis: dict) -> dict:
        raise NotImplementedError
