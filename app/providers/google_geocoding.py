from dataclasses import dataclass

from fastapi import HTTPException, status
import httpx


@dataclass(frozen=True)
class GoogleGeocodingProvider:
    api_key: str
    client: httpx.AsyncClient

    async def geocode(self, location: str) -> dict:
        response = await self.client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": location, "key": self.api_key, "language": "pt-BR"},
        )
        response.raise_for_status()
        payload = response.json()

        api_status = payload.get("status")
        if api_status != "OK":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Geocoding failed: {api_status}",
            )

        result = payload["results"][0]
        geometry = result["geometry"]["location"]
        return {
            "formatted_address": result.get("formatted_address"),
            "latitude": geometry["lat"],
            "longitude": geometry["lng"],
            "place_id": result.get("place_id"),
        }
