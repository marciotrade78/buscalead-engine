from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class GoogleSuggestProvider:
    client: httpx.AsyncClient

    async def suggest(self, query: str, language: str = "pt-BR") -> list[str]:
        raise NotImplementedError
