class DigitalPresenceAnalyzer:
    def analyze(self, lead: dict) -> dict:
        issues: list[str] = []
        strengths: list[str] = []
        recommended_actions: list[str] = []

        has_website = bool(lead.get("website"))
        has_phone = bool(lead.get("phone"))
        rating = lead.get("rating")
        review_count = lead.get("review_count") or 0

        if has_website:
            strengths.append("Possui site publicado")
        else:
            issues.append("Nao possui site cadastrado no Google")
            recommended_actions.append("Oferecer criacao de landing page ou site institucional")

        if has_phone:
            strengths.append("Possui telefone publico")
        else:
            issues.append("Nao possui telefone publico cadastrado")
            recommended_actions.append("Corrigir cadastro local para facilitar contato de clientes")

        if rating is None:
            issues.append("Nao possui nota publica no Google")
            recommended_actions.append("Criar rotina para solicitar avaliacoes de clientes")
        elif rating < 4.0:
            issues.append("Nota abaixo de 4.0 no Google")
            recommended_actions.append("Atuar em reputacao local e respostas a avaliacoes")
        else:
            strengths.append("Nota publica positiva no Google")

        if review_count < 10:
            issues.append("Poucas avaliacoes publicas")
            recommended_actions.append("Implantar campanha simples de captacao de reviews")
        elif review_count >= 50:
            strengths.append("Volume relevante de avaliacoes")

        if not issues:
            recommended_actions.append("Aprofundar SEO local e campanhas para capturar mais demanda")

        presence_level = "strong"
        if len(issues) >= 3:
            presence_level = "weak"
        elif len(issues) >= 1:
            presence_level = "medium"

        return {
            "presence_level": presence_level,
            "issues": issues,
            "strengths": strengths,
            "recommended_actions": recommended_actions,
            "signals": {
                "has_website": has_website,
                "has_phone": has_phone,
                "rating": rating,
                "review_count": review_count,
            },
        }
