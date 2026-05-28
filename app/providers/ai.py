from dataclasses import dataclass
import json
from typing import Any, Protocol

import httpx

PLACEHOLDER_KEYS = {"", "replace-me", "changeme"}


class AiProvider(Protocol):
    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]: ...


def has_configured_key(api_key: str | None) -> bool:
    return bool(api_key and api_key.strip() not in PLACEHOLDER_KEYS)


@dataclass(frozen=True)
class OpenAiProvider:
    api_key: str
    model: str
    client: httpx.AsyncClient

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _system_prompt(schema)},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _safe_json_loads(content)


@dataclass(frozen=True)
class GeminiProvider:
    api_key: str
    model: str
    client: httpx.AsyncClient

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{_system_prompt(schema)}\n\n{prompt}"}],
                    }
                ],
                "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"},
            },
        )
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _safe_json_loads(content)


@dataclass(frozen=True)
class AnthropicProvider:
    api_key: str
    model: str
    client: httpx.AsyncClient

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": self.model,
                "max_tokens": 900,
                "temperature": 0.3,
                "system": _system_prompt(schema),
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        content = "".join(
            block.get("text", "") for block in response.json().get("content", []) if block.get("type") == "text"
        )
        return _safe_json_loads(content)


@dataclass(frozen=True)
class FallbackAiProvider:
    reason: str = "AI provider is not configured"

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        del prompt, schema
        return {
            "status": "fallback",
            "provider": "local",
            "summary": "Diagnostico gerado por regras locais. Configure uma API de IA para texto mais persuasivo.",
            "sales_angle": "Priorizar os sinais objetivos mais fortes: site, reviews, telefone, SEO e diferenca frente aos concorrentes.",
            "recommended_pitch": "Apresente os pontos fracos detectados e conecte cada ajuste a captacao de clientes locais.",
            "whatsapp_message": "Oi, tudo bem? Analisei alguns pontos da presenca online da empresa e encontrei oportunidades simples para melhorar captacao local.",
            "objection_handling": "Se ja existe demanda, a proposta e transformar essa demanda em mais contatos qualificados com ajustes mensuraveis.",
            "next_best_actions": [
                "Validar dados publicos do lead",
                "Priorizar oportunidade de maior impacto",
                "Enviar abordagem curta com um insight especifico",
            ],
            "reason": self.reason,
        }


def select_ai_provider(
    settings: Any,
    client: httpx.AsyncClient,
) -> tuple[str, AiProvider]:
    if has_configured_key(settings.openai_api_key):
        return "openai", OpenAiProvider(settings.openai_api_key, settings.openai_model, client)
    if has_configured_key(settings.gemini_api_key):
        return "gemini", GeminiProvider(settings.gemini_api_key, settings.gemini_model, client)
    if has_configured_key(settings.anthropic_api_key):
        return "anthropic", AnthropicProvider(settings.anthropic_api_key, settings.anthropic_model, client)
    return "local", FallbackAiProvider()


def ai_insights_schema() -> dict[str, Any]:
    return {
        "status": "generated|fallback",
        "summary": "short executive diagnosis in Portuguese",
        "sales_angle": "commercial angle for the seller",
        "recommended_pitch": "short consultative pitch",
        "whatsapp_message": "ready-to-send WhatsApp opener",
        "objection_handling": "answer to a likely objection",
        "next_best_actions": ["action 1", "action 2", "action 3"],
    }


def build_ai_prompt(diagnosis: dict[str, Any]) -> str:
    compact = {
        "lead": diagnosis.get("lead"),
        "digital_presence": diagnosis.get("digital_presence"),
        "seo": _compact_seo(diagnosis.get("seo") or {}),
        "competitive": diagnosis.get("competitive"),
        "keywords": (diagnosis.get("keywords") or {}).get("terms", [])[:8],
        "opportunity": diagnosis.get("opportunity"),
    }
    return (
        "Gere um diagnostico comercial em portugues do Brasil para venda consultiva. "
        "Use apenas os dados fornecidos, seja especifico, nao invente numeros, e retorne somente JSON.\n\n"
        f"Dados:\n{json.dumps(compact, ensure_ascii=False)}"
    )


def normalize_ai_insights(provider_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "status": payload.get("status") or "generated",
        "provider": payload.get("provider") or provider_name,
        "summary": payload.get("summary") or "",
        "sales_angle": payload.get("sales_angle") or "",
        "recommended_pitch": payload.get("recommended_pitch") or "",
        "whatsapp_message": payload.get("whatsapp_message") or "",
        "objection_handling": payload.get("objection_handling") or "",
        "next_best_actions": payload.get("next_best_actions") or [],
    }
    if "reason" in payload:
        result["reason"] = payload["reason"]
    return result


def _system_prompt(schema: dict[str, Any]) -> str:
    return (
        "Voce e um especialista em inteligencia comercial local para agencias e vendedores. "
        "Responda em portugues do Brasil, em JSON valido, seguindo este schema conceitual: "
        f"{json.dumps(schema, ensure_ascii=False)}"
    )


def _compact_seo(seo: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": seo.get("status"),
        "issues": seo.get("issues"),
        "opportunities": seo.get("opportunities"),
        "signals": seo.get("signals"),
        "pagespeed": seo.get("pagespeed"),
    }


def _safe_json_loads(content: str) -> dict[str, Any]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        payload = json.loads(content[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("AI response must be a JSON object")
    return payload
