class KeywordResearchAnalyzer:
    def analyze(self, niche: str, location: str, suggestions: list[str] | None = None) -> dict:
        clean_niche = niche.strip().lower()
        clean_location = location.strip()
        base_terms = [
            f"{clean_niche} em {clean_location}",
            f"{clean_niche} perto de mim",
            f"melhor {clean_niche} {clean_location}",
            f"{clean_niche} aberto agora {clean_location}",
            f"orcamento {clean_niche} {clean_location}",
        ]
        all_terms = self._dedupe(base_terms + (suggestions or []))

        return {
            "niche": niche,
            "location": location,
            "terms": [
                {
                    "keyword": term,
                    "source": "suggest" if term not in base_terms else "base",
                    "intent": self._intent_for(term),
                    "difficulty": self._difficulty_for(term),
                }
                for term in all_terms
            ],
            "summary": "Termos locais com intencao comercial para priorizar conteudo e campanhas.",
        }

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

    @staticmethod
    def _intent_for(term: str) -> str:
        lower = term.lower()
        if "orcamento" in lower or "preco" in lower or "valor" in lower:
            return "transactional"
        if "perto de mim" in lower or "aberto agora" in lower:
            return "high"
        if "melhor" in lower:
            return "medium"
        return "local_discovery"

    @staticmethod
    def _difficulty_for(term: str) -> str:
        lower = term.lower()
        if "perto de mim" in lower or "aberto agora" in lower or "melhor" in lower:
            return "medium"
        return "low"
