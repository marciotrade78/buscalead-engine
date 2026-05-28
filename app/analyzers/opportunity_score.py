class OpportunityScoreAnalyzer:
    def calculate(self, signals: dict) -> dict:
        score = 0
        reasons: list[str] = []

        digital = signals.get("digital_presence", {}).get("signals", {})
        seo = signals.get("seo", {})
        competitive = signals.get("competitive", {})

        if not digital.get("has_website"):
            score += 35
            reasons.append("Sem site cadastrado")
        if not digital.get("has_phone"):
            score += 10
            reasons.append("Telefone ausente")

        rating = digital.get("rating")
        if rating is None:
            score += 15
            reasons.append("Sem nota publica")
        elif rating < 4.0:
            score += 20
            reasons.append("Nota abaixo de 4.0")

        review_count = digital.get("review_count") or 0
        if review_count < 10:
            score += 20
            reasons.append("Poucas avaliacoes")
        elif review_count < 30:
            score += 10
            reasons.append("Volume moderado de avaliacoes")

        if seo.get("status") == "missing_website":
            score += 10
        elif seo.get("issues"):
            score += min(15, len(seo["issues"]) * 5)
            reasons.append("Problemas basicos de SEO detectados")

        competitive_issues = competitive.get("issues") or []
        if competitive.get("status") == "compared" and competitive_issues:
            score += min(15, len(competitive_issues) * 5)
            reasons.append("Desvantagens frente a concorrentes locais")

        score = min(score, 100)
        priority = "low"
        if score >= 70:
            priority = "high"
        elif score >= 40:
            priority = "medium"

        return {
            "score": score,
            "priority": priority,
            "reasons": reasons,
        }
