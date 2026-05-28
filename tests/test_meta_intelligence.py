import pytest

from app.providers.meta_intelligence import MetaIntelligenceProvider


@pytest.mark.asyncio
async def test_meta_intelligence_flags_missing_public_assets() -> None:
    payload = await MetaIntelligenceProvider().collect_signals(
        {
            "name": "Clinica Sinal",
            "category": "dentistas",
            "address": "Curitiba",
            "website": None,
            "phone": None,
            "rating": 3.7,
            "review_count": 4,
        }
    )

    signal_types = {signal["type"] for signal in payload["signals"]}

    assert payload["status"] == "generated"
    assert payload["data_quality"] == "medium"
    assert "missing_website" in signal_types
    assert "missing_phone" in signal_types
    assert "low_rating" in signal_types
    assert "low_review_volume" in signal_types
    assert payload["conversion_hooks"]
    assert "Reputacao fragil" in payload["risk_flags"]


@pytest.mark.asyncio
async def test_meta_intelligence_returns_baseline_for_complete_lead() -> None:
    payload = await MetaIntelligenceProvider().collect_signals(
        {
            "name": "Clinica Forte",
            "category": "dentistas",
            "address": "Curitiba",
            "website": "https://example.com",
            "phone": "41999999999",
            "rating": 4.8,
            "review_count": 80,
        }
    )

    assert payload["data_quality"] == "high"
    assert payload["signals"] == [
        {
            "type": "baseline_ok",
            "label": "Base publica consistente",
            "insight": "Oportunidade tende a estar em SEO local, conteudo e conversao.",
        }
    ]
