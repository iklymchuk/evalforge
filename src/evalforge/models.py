"""Pydantic models for evalforge core types."""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int


class ProviderResponse(BaseModel):
    """Normalized response from any LLM provider."""

    provider: Literal["openai", "anthropic", "together"]
    model: str
    text: str
    usage: TokenUsage
    latency_ms: int
    raw: dict = Field(default_factory=dict)  # Provider-specific raw response


class PromptRun(BaseModel):
    """A single prompt sent to a provider, with its response."""

    id: str  # UUID
    timestamp: datetime
    system_prompt: str | None
    user_prompt: str
    response: ProviderResponse


class BatchJob(BaseModel):
    """One prompt to run against one provider"""

    provider: Literal["openai", "anthropic", "together"]
    user_prompt: str
    system_prompt: str | None = None
    model: str | None = None
    max_tokens: int = 1024
    temperature: float = 1.0


class JobResult(BaseModel):
    """Outcome of one job: either a response or an error string."""

    job: BatchJob
    response: ProviderResponse | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.response is not None


class BatchResult(BaseModel):
    """All outcomes for one batch, plus cnvenience aggregates."""

    batch_id: str
    results: list[JobResult]

    @property
    def succeeded(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.ok)

    @property
    def total_output_tokens(self) -> int:
        return sum(r.response.usage.output_tokens for r in self.results if r.ok)
