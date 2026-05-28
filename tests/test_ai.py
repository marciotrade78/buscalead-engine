from types import SimpleNamespace

import httpx
import pytest

from app.providers.ai import (
    FallbackAiProvider,
    _safe_json_loads,
    build_ai_prompt,
    has_configured_key,
    normalize_ai_insights,
    select_ai_provider,
)


@pytest.mark.asyncio
async def test_fallback_ai_provider_returns_sales_fields() -> None:
    payload = await FallbackAiProvider().generate_json("prompt", {})

    assert payload["status"] == "fallback"
    assert payload["provider"] == "local"
    assert payload["whatsapp_message"]
    assert payload["next_best_actions"]


def test_select_ai_provider_prefers_openai_when_configured() -> None:
    settings = SimpleNamespace(
        openai_api_key="sk-test",
        openai_model="gpt-4o-mini",
        gemini_api_key="gemini-test",
        gemini_model="gemini-1.5-flash",
        anthropic_api_key="anthropic-test",
        anthropic_model="claude-3-5-haiku-latest",
    )

    client = httpx.AsyncClient()
    provider_name, _provider = select_ai_provider(settings, client)

    assert provider_name == "openai"


def test_select_ai_provider_uses_local_for_placeholder_keys() -> None:
    settings = SimpleNamespace(
        openai_api_key="replace-me",
        openai_model="gpt-4o-mini",
        gemini_api_key="",
        gemini_model="gemini-1.5-flash",
        anthropic_api_key="changeme",
        anthropic_model="claude-3-5-haiku-latest",
    )

    client = httpx.AsyncClient()
    provider_name, _provider = select_ai_provider(settings, client)

    assert provider_name == "local"
    assert has_configured_key("replace-me") is False


def test_build_ai_prompt_compacts_diagnosis() -> None:
    prompt = build_ai_prompt(
        {
            "lead": {"name": "Clinica Teste"},
            "seo": {"page": {"html": "ignored"}, "issues": ["Sem meta"]},
            "keywords": {"terms": [{"keyword": f"termo {index}"} for index in range(10)]},
        }
    )

    assert "Clinica Teste" in prompt
    assert "termo 7" in prompt
    assert "termo 8" not in prompt
    assert "ignored" not in prompt


def test_normalize_ai_insights_fills_required_fields() -> None:
    result = normalize_ai_insights("openai", {"summary": "Resumo"})

    assert result["provider"] == "openai"
    assert result["summary"] == "Resumo"
    assert result["next_best_actions"] == []


def test_safe_json_loads_extracts_json_object_from_text() -> None:
    assert _safe_json_loads('texto antes {"summary":"ok"} texto depois') == {"summary": "ok"}
