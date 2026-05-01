"""Anthropic provider implementation."""

from evalforge.providers.base import Provider
from evalforge.models import ProviderResponse, TokenUsage
from anthropic import Anthropic
from dotenv import load_dotenv
import time

load_dotenv()

class AnthropicProvider(Provider):
    name = "anthropic"
    default_model = "claude-haiku-4-5-20251001"

    def __init__(self):
        self._client = Anthropic()

    def complete(
        self, 
        user_prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        ) -> ProviderResponse:

        start = time.perf_counter()
        kwargs = {
            "model": model or self.default_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)

        return ProviderResponse(
            provider=self.name,
            model=response.model,
            text=response.content[0].text,
            usage=TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
            latency_ms=latency_ms,
            raw=response.model_dump(),
        )