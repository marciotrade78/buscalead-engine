from dataclasses import dataclass
from typing import Any, Protocol


class AiProvider(Protocol):
    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class OpenAiProvider:
    api_key: str

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class GeminiProvider:
    api_key: str

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class AnthropicProvider:
    api_key: str

    async def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
