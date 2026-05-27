from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class PageSpeedProvider:
    api_key: str
    client: httpx.AsyncClient

    async def analyze_url(self, url: str) -> dict:
        raise NotImplementedError
