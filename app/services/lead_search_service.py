import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.core.config import settings
from app.providers.google_geocoding import GoogleGeocodingProvider
from app.providers.google_places import GooglePlacesProvider
from app.repositories.leads import LeadRepository
from app.schemas.common import JobAcceptedResponse
from app.schemas.leads import LeadSearchRequest, LeadSearchResultResponse


class LeadSearchService:
    def queue_search(self, payload: LeadSearchRequest, current_user: CurrentUser) -> JobAcceptedResponse:
        from app.jobs.lead_jobs import search_leads_job

        job = search_leads_job.delay(payload.model_dump(), current_user.user_id)
        return JobAcceptedResponse(
            job_id=job.id,
            message="Lead search queued",
        )

    def queue_refresh(self, lead_id: str, current_user: CurrentUser) -> JobAcceptedResponse:
        from app.jobs.lead_jobs import refresh_lead_job

        job = refresh_lead_job.delay(lead_id, current_user.user_id)
        return JobAcceptedResponse(
            job_id=job.id,
            message="Lead refresh queued",
        )

    def queue_analysis(self, lead_id: str, current_user: CurrentUser) -> JobAcceptedResponse:
        from app.jobs.analysis_jobs import analyze_lead_job

        job = analyze_lead_job.delay(lead_id, current_user.user_id)
        return JobAcceptedResponse(
            job_id=job.id,
            message="Lead analysis queued",
        )

    async def search_now(
        self,
        payload: LeadSearchRequest,
        current_user: CurrentUser,
        session: AsyncSession,
        persist: bool = True,
    ) -> LeadSearchResultResponse:
        if not settings.google_places_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_PLACES_API_KEY is not configured",
            )

        async with httpx.AsyncClient(timeout=30) as client:
            geocoding = GoogleGeocodingProvider(api_key=settings.google_places_api_key, client=client)
            places = GooglePlacesProvider(api_key=settings.google_places_api_key, client=client)

            location_data = await geocoding.geocode(payload.location)
            query = f"{payload.niche} em {payload.location}"
            search_results = await places.search_places(
                query=query,
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                radius_meters=payload.radius_meters,
                limit=payload.limit,
            )

            leads = []
            repository = LeadRepository(session) if persist else None
            for item in search_results:
                place_id = item.get("place_id")
                if not place_id:
                    continue
                details = await places.get_place_details(place_id)
                normalized = self.normalize_place(details)
                if repository:
                    leads.append(await repository.upsert_from_place(normalized, current_user.user_id))
                else:
                    leads.append({"id": place_id, **normalized})

            if persist:
                await session.commit()

        return LeadSearchResultResponse(
            query=query,
            location=payload.location,
            total=len(leads),
            leads=leads,
        )

    async def refresh_now(
        self,
        lead_id: str,
        current_user: CurrentUser,
        session: AsyncSession,
    ) -> dict:
        if not settings.google_places_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_PLACES_API_KEY is not configured",
            )

        repository = LeadRepository(session)
        lead = await repository.get_by_id(lead_id, current_user.user_id)
        if lead is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

        google_place_id = lead.get("google_place_id")
        if not google_place_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Lead does not have a google_place_id to refresh",
            )

        async with httpx.AsyncClient(timeout=30) as client:
            places = GooglePlacesProvider(api_key=settings.google_places_api_key, client=client)
            details = await places.get_place_details(google_place_id)

        normalized = self.normalize_place(details)
        refreshed = await repository.update_from_place(lead_id, current_user.user_id, normalized)
        await session.commit()
        return refreshed or {}

    async def list_leads(self, current_user: CurrentUser, session: AsyncSession) -> list[dict]:
        return await LeadRepository(session).list_by_user(current_user.user_id)

    @staticmethod
    def normalize_place(place: dict) -> dict:
        geometry = place.get("geometry", {}).get("location", {})
        types = place.get("types") or []
        return {
            "google_place_id": place.get("place_id"),
            "name": place["name"],
            "address": place.get("formatted_address"),
            "phone": place.get("formatted_phone_number") or place.get("international_phone_number"),
            "website": place.get("website"),
            "rating": place.get("rating"),
            "review_count": place.get("user_ratings_total"),
            "category": types[0] if types else None,
            "latitude": geometry.get("lat"),
            "longitude": geometry.get("lng"),
        }
