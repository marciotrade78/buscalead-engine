class MetaIntelligenceProvider:
    async def collect_signals(self, lead: dict) -> dict:
        signals: list[dict[str, str]] = []
        risk_flags: list[str] = []
        conversion_hooks: list[str] = []

        name = lead.get("name") or "Lead"
        category = lead.get("category") or "empresa local"
        location = lead.get("address") or lead.get("city") or "regiao local"
        has_website = bool(lead.get("website"))
        has_phone = bool(lead.get("phone"))
        rating = lead.get("rating")
        review_count = lead.get("review_count") or 0

        if not has_website:
            signals.append(
                {
                    "type": "missing_website",
                    "label": "Sem site cadastrado",
                    "insight": "Pode estar perdendo demanda local para concorrentes com presenca propria.",
                }
            )
            conversion_hooks.append("Abrir conversa oferecendo uma landing page local focada em captacao.")

        if not has_phone:
            signals.append(
                {
                    "type": "missing_phone",
                    "label": "Telefone ausente",
                    "insight": "O caminho de contato esta menos direto para clientes prontos para comprar.",
                }
            )
            risk_flags.append("Contato publico incompleto")

        if rating is None:
            signals.append(
                {
                    "type": "missing_rating",
                    "label": "Sem nota publica",
                    "insight": "Falta prova social visivel para quem compara opcoes locais.",
                }
            )
            conversion_hooks.append("Sugerir rotina simples para coletar as primeiras avaliacoes.")
        elif rating < 4.0:
            signals.append(
                {
                    "type": "low_rating",
                    "label": "Nota abaixo de 4.0",
                    "insight": "A reputacao pode estar reduzindo conversao mesmo quando ha demanda.",
                }
            )
            risk_flags.append("Reputacao fragil")

        if review_count < 10:
            signals.append(
                {
                    "type": "low_review_volume",
                    "label": "Poucas avaliacoes",
                    "insight": "Baixo volume de reviews dificulta confianca e ranqueamento local.",
                }
            )
            conversion_hooks.append("Propor campanha de reviews com mensagem curta para clientes recentes.")

        if not signals:
            signals.append(
                {
                    "type": "baseline_ok",
                    "label": "Base publica consistente",
                    "insight": "Oportunidade tende a estar em SEO local, conteudo e conversao.",
                }
            )
            conversion_hooks.append("Posicionar a abordagem como otimizacao para capturar mais demanda qualificada.")

        return {
            "status": "generated",
            "lead_name": name,
            "category": category,
            "location": location,
            "signals": signals,
            "risk_flags": risk_flags,
            "conversion_hooks": conversion_hooks[:3],
            "data_quality": self._data_quality(has_website, has_phone, rating, review_count),
        }

    @staticmethod
    def _data_quality(has_website: bool, has_phone: bool, rating: float | None, review_count: int) -> str:
        populated = sum([has_website, has_phone, rating is not None, review_count > 0])
        if populated >= 3:
            return "high"
        if populated == 2:
            return "medium"
        return "low"
