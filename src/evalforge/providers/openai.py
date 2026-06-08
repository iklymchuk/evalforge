"""OpenAI provider implementation."""

from evalforge.providers.base import Provider
from evalforge.models import ProviderResponse, TokenUsage
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()


class OpenAIProvider(Provider):
    name = "openai"
    default_model = "gpt-4o-mini"

    def __init__(self):
        self._client = OpenAI()

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
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if system_prompt:
            kwargs["messages"] = [
                {"role": "system", "content": system_prompt}
            ] + kwargs["messages"]

        response = self._client.chat.completions.create(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)

        return ProviderResponse(
            provider=self.name,
            model=response.model,
            text=response.choices[0].message.content,
            usage=TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            ),
            latency_ms=latency_ms,
            raw=response.model_dump(),
        )
