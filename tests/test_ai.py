from types import SimpleNamespace

import json

import httpx
import pytest

from app.providers.ai import (
    FallbackAiProvider,
    _safe_json_loads,
    build_ai_prompt,
    has_configured_key,
    normalize_ai_insights,
    select_ai_provider,
    CustomChatCompletionsProvider,
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
        custom_llm_api_key="",
        custom_llm_base_url="",
        custom_llm_model="",
        custom_llm_provider_name="custom_llm",
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
        custom_llm_api_key="",
        custom_llm_base_url="",
        custom_llm_model="",
        custom_llm_provider_name="custom_llm",
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


def test_select_ai_provider_prefers_custom_llm_when_configured() -> None:
    settings = SimpleNamespace(
        custom_llm_api_key="llm-test",
        custom_llm_base_url="https://llm.example.com/v1",
        custom_llm_model="sales-model",
        custom_llm_provider_name="minha_api",
        openai_api_key="sk-test",
        openai_model="gpt-4o-mini",
        gemini_api_key="gemini-test",
        gemini_model="gemini-1.5-flash",
        anthropic_api_key="anthropic-test",
        anthropic_model="claude-3-5-haiku-latest",
    )

    client = httpx.AsyncClient()
    provider_name, provider = select_ai_provider(settings, client)

    assert provider_name == "minha_api"
    assert isinstance(provider, CustomChatCompletionsProvider)


@pytest.mark.asyncio
async def test_custom_chat_completions_provider_parses_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://llm.example.com/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer llm-test"
        payload = json.loads(request.content)
        assert payload["model"] == "sales-model"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"summary":"ok","next_best_actions":["agir"]}'
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        payload = await CustomChatCompletionsProvider(
            api_key="llm-test",
            base_url="https://llm.example.com/v1",
            model="sales-model",
            provider_name="minha_api",
            client=client,
        ).generate_json("prompt", {})

    assert payload == {
        "summary": "ok",
        "next_best_actions": ["agir"],
        "provider": "minha_api",
    }


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
