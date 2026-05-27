from dataclasses import dataclass

from fastapi import HTTPException, status
import httpx


@dataclass(frozen=True)
class GooglePlacesProvider:
    api_key: str
    client: httpx.AsyncClient

    async def search_places(
        self,
        query: str,
        latitude: float,
        longitude: float,
        radius_meters: int,
        limit: int,
    ) -> list[dict]:
        response = await self.client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                "query": query,
                "location": f"{latitude},{longitude}",
                "radius": radius_meters,
                "key": self.api_key,
                "language": "pt-BR",
            },
        )
        response.raise_for_status()
        payload = response.json()

        api_status = payload.get("status")
        if api_status not in {"OK", "ZERO_RESULTS"}:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Places Text Search failed: {api_status}",
            )

        return payload.get("results", [])[:limit]

    async def get_place_details(self, place_id: str) -> dict:
        response = await self.client.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": ",".join(
                    [
                        "place_id",
                        "name",
                        "formatted_address",
                        "formatted_phone_number",
                        "international_phone_number",
                        "website",
                        "rating",
                        "user_ratings_total",
                        "types",
                        "geometry",
                        "business_status",
                        "url",
                    ]
                ),
                "key": self.api_key,
                "language": "pt-BR",
            },
        )
        response.raise_for_status()
        payload = response.json()

        api_status = payload.get("status")
        if api_status != "OK":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Place Details failed: {api_status}",
            )

        return payload["result"]
