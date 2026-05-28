from fastapi import HTTPException, status
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.competitive import CompetitiveAnalyzer
from app.analyzers.digital_presence import DigitalPresenceAnalyzer
from app.analyzers.keywords import KeywordResearchAnalyzer
from app.analyzers.opportunity_score import OpportunityScoreAnalyzer
from app.analyzers.seo import SeoAnalyzer
from app.auth.dependencies import CurrentUser
from app.core.config import settings
from app.providers.ai import (
    FallbackAiProvider,
    ai_insights_schema,
    build_ai_prompt,
    normalize_ai_insights,
    select_ai_provider,
)
from app.providers.google_suggest import GoogleSuggestProvider
from app.providers.pagespeed import PageSpeedProvider
from app.providers.web_scraper import WebScraperProvider
from app.repositories.analyses import AnalysisRepository
from app.repositories.leads import LeadRepository


class AnalysisService:
    def __init__(self) -> None:
        self.digital_presence = DigitalPresenceAnalyzer()
        self.competitive = CompetitiveAnalyzer()
        self.seo = SeoAnalyzer()
        self.opportunity_score = OpportunityScoreAnalyzer()
        self.keywords = KeywordResearchAnalyzer()

    async def analyze_lead(
        self,
        lead_id: str,
        current_user: CurrentUser,
        session: AsyncSession,
        persist: bool = True,
    ) -> dict:
        lead = await LeadRepository(session).get_by_id(lead_id, current_user.user_id)
        if lead is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

        repository = LeadRepository(session)
        competitors = await repository.list_competitors(lead, current_user.user_id)
        competitive = self.competitive.compare(lead, competitors)
        digital_presence = self.digital_presence.analyze(lead)
        page_data = await self._fetch_page_data(lead)
        pagespeed_data = await self._fetch_pagespeed_data(lead)
        seo = self.seo.analyze(lead, page_data=page_data, pagespeed_data=pagespeed_data)
        opportunity = self.opportunity_score.calculate(
            {
                "digital_presence": digital_presence,
                "seo": seo,
                "competitive": competitive,
            }
        )
        keyword_niche = lead.get("category") or lead.get("name") or "empresa local"
        keyword_location = lead.get("address") or "regiao local"
        keyword_suggestions = await self._fetch_keyword_suggestions(keyword_niche, keyword_location)
        keyword_research = self.keywords.analyze(
            niche=keyword_niche,
            location=keyword_location,
            suggestions=keyword_suggestions,
        )
        diagnosis = {
            "lead": lead,
            "digital_presence": digital_presence,
            "seo": seo,
            "competitive": competitive,
            "keywords": keyword_research,
            "opportunity": opportunity,
            "summary": self._build_summary(lead, opportunity),
        }
        diagnosis["ai_insights"] = await self._generate_ai_insights(diagnosis)

        if not persist:
            return diagnosis

        saved = await AnalysisRepository(session).save_diagnosis(
            lead_id=lead_id,
            user_id=current_user.user_id,
            diagnosis=diagnosis,
        )
        await session.commit()
        return saved


    async def _generate_ai_insights(self, diagnosis: dict) -> dict:
        schema = ai_insights_schema()
        prompt = build_ai_prompt(diagnosis)
        async with httpx.AsyncClient(timeout=45) as client:
            provider_name, provider = select_ai_provider(settings, client)
            try:
                payload = await provider.generate_json(prompt, schema)
            except Exception as exc:
                fallback = FallbackAiProvider(reason=f"AI provider failed: {exc}")
                payload = await fallback.generate_json(prompt, schema)
                provider_name = "local"
        return normalize_ai_insights(provider_name, payload)

    async def _fetch_keyword_suggestions(self, niche: str, location: str) -> list[str]:
        query = f"{niche} {location}"
        async with httpx.AsyncClient(timeout=10) as client:
            return await GoogleSuggestProvider(client=client).suggest(query)

    async def _fetch_page_data(self, lead: dict) -> dict | None:
        website = lead.get("website")
        if not website:
            return None
        return await WebScraperProvider().fetch_page_data(website)

    async def _fetch_pagespeed_data(self, lead: dict) -> dict | None:
        website = lead.get("website")
        if not website:
            return None
        async with httpx.AsyncClient(timeout=45) as client:
            return await PageSpeedProvider(
                api_key=settings.pagespeed_api_key,
                client=client,
            ).analyze_url(website)

    @staticmethod
    def _build_summary(lead: dict, opportunity: dict) -> str:
        priority = opportunity.get("priority", "low")
        score = opportunity.get("score", 0)
        name = lead.get("name", "Lead")
        if priority == "high":
            return f"{name} tem alta oportunidade comercial, com score {score}/100."
        if priority == "medium":
            return f"{name} tem oportunidade moderada, com score {score}/100."
        return f"{name} tem baixa urgencia aparente, com score {score}/100."
