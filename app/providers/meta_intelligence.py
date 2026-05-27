class MetaIntelligenceProvider:
    async def collect_signals(self, lead: dict) -> dict:
        raise NotImplementedError
