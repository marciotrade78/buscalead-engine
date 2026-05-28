from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class GoogleSuggestProvider:
    client: httpx.AsyncClient

    async def suggest(self, query: str, language: str = "pt-BR") -> list[str]:
        try:
            response = await self.client.get(
                "https://suggestqueries.google.com/complete/search",
                params={
                    "client": "firefox",
                    "q": query,
                    "hl": language,
                },
                headers={"User-Agent": "BuscaLeadBot/0.1"},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError, TypeError):
            return []

        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            return []

        suggestions = [item for item in payload[1] if isinstance(item, str)]
        return self._dedupe(suggestions)

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = " ".join(item.split()).strip()
            key = normalized.lower()
            if not normalized or key in seen:
                continue
            seen.add(key)
            result.append(normalized)
        return result
