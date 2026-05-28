from dataclasses import dataclass

from fastapi import HTTPException, status
import httpx


@dataclass(frozen=True)
class PageSpeedProvider:
    api_key: str
    client: httpx.AsyncClient

    async def analyze_url(self, url: str) -> dict:
        if not self._has_configured_key():
            return {"status": "skipped", "reason": "PAGESPEED_API_KEY is not configured"}

        try:
            response = await self.client.get(
                "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                params={
                    "url": url,
                    "key": self.api_key,
                    "strategy": "mobile",
                    "category": ["performance", "seo", "accessibility", "best-practices"],
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return {"status": "failed", "error": str(exc)}
        payload = response.json()
        lighthouse = payload.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})

        if not lighthouse:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="PageSpeed response did not include lighthouseResult",
            )

        return {
            "status": "checked",
            "final_url": lighthouse.get("finalDisplayedUrl") or payload.get("id"),
            "scores": {
                name: self._normalize_score(category.get("score"))
                for name, category in categories.items()
            },
            "audits": self._extract_audits(lighthouse.get("audits", {})),
        }

    def _has_configured_key(self) -> bool:
        return bool(self.api_key and self.api_key.strip() not in {"replace-me", "changeme"})

    @staticmethod
    def _normalize_score(score: float | int | None) -> int | None:
        if score is None:
            return None
        return round(float(score) * 100)

    @staticmethod
    def _extract_audits(audits: dict) -> dict:
        wanted = [
            "first-contentful-paint",
            "largest-contentful-paint",
            "cumulative-layout-shift",
            "interactive",
            "total-blocking-time",
        ]
        return {
            key: {
                "title": audits.get(key, {}).get("title"),
                "display_value": audits.get(key, {}).get("displayValue"),
                "score": PageSpeedProvider._normalize_score(audits.get(key, {}).get("score")),
            }
            for key in wanted
            if key in audits
        }
