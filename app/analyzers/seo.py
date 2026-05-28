class SeoAnalyzer:
    def analyze(
        self,
        lead: dict,
        page_data: dict | None = None,
        pagespeed_data: dict | None = None,
    ) -> dict:
        if not lead.get("website"):
            return {
                "status": "missing_website",
                "issues": ["Lead sem site para analise SEO"],
                "opportunities": ["Criar site otimizado para buscas locais"],
                "signals": {"has_title": False, "has_meta_description": False, "has_h1": False},
                "pagespeed": pagespeed_data,
            }

        if page_data and page_data.get("status") == "fetch_failed":
            return {
                "status": "fetch_failed",
                "issues": ["Nao foi possivel acessar o site para analise SEO"],
                "opportunities": ["Verificar disponibilidade, SSL e bloqueios do site"],
                "signals": {},
                "page_error": page_data.get("error"),
                "pagespeed": pagespeed_data,
            }

        if not page_data:
            return {
                "status": "not_checked",
                "issues": [],
                "opportunities": ["Executar auditoria de SEO tecnico e conteudo local"],
                "signals": {},
                "pagespeed": pagespeed_data,
            }

        title = (page_data.get("title") or "").strip()
        meta_description = (page_data.get("meta_description") or "").strip()
        h1 = (page_data.get("h1") or "").strip()
        canonical = (page_data.get("canonical") or "").strip()
        scores = (pagespeed_data or {}).get("scores", {})

        issues: list[str] = []
        opportunities: list[str] = []

        if not title:
            issues.append("Pagina sem title detectavel")
            opportunities.append("Criar title com servico e cidade")
        elif len(title) < 20:
            issues.append("Title muito curto")
            opportunities.append("Reescrever title com servico, diferencial e localizacao")

        if not meta_description:
            issues.append("Pagina sem meta description detectavel")
            opportunities.append("Adicionar meta description voltada a conversao")
        elif len(meta_description) < 70:
            issues.append("Meta description muito curta")
            opportunities.append("Expandir meta description com oferta e chamada para contato")

        if not h1:
            issues.append("Pagina sem H1 detectavel")
            opportunities.append("Adicionar H1 claro com oferta principal")

        if not canonical:
            issues.append("Canonical nao detectado")
            opportunities.append("Adicionar canonical para reduzir ambiguidade de indexacao")

        performance_score = scores.get("performance")
        seo_score = scores.get("seo")
        if performance_score is not None and performance_score < 60:
            issues.append("Performance mobile baixa no PageSpeed")
            opportunities.append("Otimizar velocidade mobile e Core Web Vitals")
        if seo_score is not None and seo_score < 80:
            issues.append("Score SEO baixo no PageSpeed")
            opportunities.append("Corrigir problemas tecnicos apontados pelo Lighthouse")

        return {
            "status": "checked",
            "issues": issues,
            "opportunities": opportunities,
            "signals": {
                "has_title": bool(title),
                "has_meta_description": bool(meta_description),
                "has_h1": bool(h1),
                "has_canonical": bool(canonical),
                "title_length": len(title),
                "meta_description_length": len(meta_description),
                "performance_score": performance_score,
                "seo_score": seo_score,
            },
            "page": page_data,
            "pagespeed": pagespeed_data,
        }
