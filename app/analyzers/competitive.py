class CompetitiveAnalyzer:
    def compare(self, lead: dict, competitors: list[dict]) -> dict:
        sample = [item for item in competitors if item.get("id") != lead.get("id")]
        if not sample:
            return {
                "status": "insufficient_data",
                "sample_size": 0,
                "issues": [],
                "advantages": [],
                "opportunities": ["Buscar mais concorrentes para comparacao local"],
                "benchmarks": {},
            }

        ratings = [item["rating"] for item in sample if item.get("rating") is not None]
        review_counts = [item.get("review_count") or 0 for item in sample]
        competitors_with_site = sum(1 for item in sample if item.get("website"))
        competitors_with_phone = sum(1 for item in sample if item.get("phone"))

        average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        average_reviews = round(sum(review_counts) / len(review_counts), 1) if review_counts else 0
        site_presence_rate = round(competitors_with_site / len(sample), 2)
        phone_presence_rate = round(competitors_with_phone / len(sample), 2)

        issues: list[str] = []
        advantages: list[str] = []
        opportunities: list[str] = []

        lead_rating = lead.get("rating")
        lead_reviews = lead.get("review_count") or 0

        if average_rating is not None and lead_rating is not None:
            if lead_rating < average_rating:
                issues.append("Nota abaixo da media dos concorrentes")
                opportunities.append("Melhorar reputacao e respostas a avaliacoes")
            elif lead_rating > average_rating:
                advantages.append("Nota acima da media dos concorrentes")
        elif lead_rating is None and average_rating is not None:
            issues.append("Sem nota enquanto concorrentes possuem avaliacao")
            opportunities.append("Estimular primeiras avaliacoes publicas")

        if lead_reviews < average_reviews:
            issues.append("Volume de avaliacoes abaixo da media local")
            opportunities.append("Criar campanha de captacao de reviews")
        elif average_reviews and lead_reviews > average_reviews:
            advantages.append("Volume de avaliacoes acima da media local")

        if not lead.get("website") and site_presence_rate >= 0.5:
            issues.append("Concorrentes possuem site com mais frequencia")
            opportunities.append("Criar site ou landing page para competir na busca local")
        elif lead.get("website") and site_presence_rate < 0.5:
            advantages.append("Possui site em mercado com baixa presenca digital")

        if not lead.get("phone") and phone_presence_rate >= 0.5:
            issues.append("Concorrentes exibem telefone com mais frequencia")
            opportunities.append("Corrigir telefone no perfil local")

        return {
            "status": "compared",
            "sample_size": len(sample),
            "issues": issues,
            "advantages": advantages,
            "opportunities": opportunities,
            "benchmarks": {
                "average_rating": average_rating,
                "average_review_count": average_reviews,
                "site_presence_rate": site_presence_rate,
                "phone_presence_rate": phone_presence_rate,
            },
            "top_competitors": self._top_competitors(sample),
        }

    @staticmethod
    def _top_competitors(competitors: list[dict]) -> list[dict]:
        ranked = sorted(
            competitors,
            key=lambda item: (item.get("rating") or 0, item.get("review_count") or 0),
            reverse=True,
        )
        return [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "rating": item.get("rating"),
                "review_count": item.get("review_count"),
                "website": item.get("website"),
            }
            for item in ranked[:5]
        ]
