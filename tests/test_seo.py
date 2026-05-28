from app.analyzers.seo import SeoAnalyzer
from app.providers.pagespeed import PageSpeedProvider
from app.providers.web_scraper import WebScraperProvider


def test_web_scraper_extracts_basic_metadata() -> None:
    html = """
    <html>
      <head>
        <title>Dentista Centro Curitiba</title>
        <meta name="description" content="Atendimento odontologico no centro de Curitiba." />
        <link rel="canonical" href="https://example.com" />
      </head>
      <body><h1>Clinica odontologica em Curitiba</h1></body>
    </html>
    """
    soup = WebScraperProvider().parse_html(html)

    assert soup.title.string == "Dentista Centro Curitiba"
    assert soup.find("h1").get_text(strip=True) == "Clinica odontologica em Curitiba"


def test_seo_analyzer_uses_pagespeed_scores() -> None:
    result = SeoAnalyzer().analyze(
        {"website": "https://example.com"},
        page_data={
            "status": "fetched",
            "title": "Dentista Centro Curitiba",
            "meta_description": "Curta",
            "h1": "Dentista em Curitiba",
            "canonical": "https://example.com",
        },
        pagespeed_data={"status": "checked", "scores": {"performance": 42, "seo": 75}},
    )

    assert result["status"] == "checked"
    assert "Performance mobile baixa no PageSpeed" in result["issues"]
    assert result["signals"]["performance_score"] == 42


def test_pagespeed_provider_normalizes_scores_and_extracts_audits() -> None:
    assert PageSpeedProvider._normalize_score(0.91) == 91
    audits = PageSpeedProvider._extract_audits(
        {
            "largest-contentful-paint": {
                "title": "Largest Contentful Paint",
                "displayValue": "3.4 s",
                "score": 0.48,
            }
        }
    )

    assert audits["largest-contentful-paint"]["score"] == 48


def test_pagespeed_provider_skips_placeholder_key() -> None:
    provider = PageSpeedProvider(api_key="replace-me", client=None)

    assert provider._has_configured_key() is False
