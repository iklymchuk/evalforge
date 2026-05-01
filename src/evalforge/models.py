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
    raw: dict = Field(default_factory=dict) # Provider-specific raw response

class PromptRun(BaseModel):
    """A single prompt sent to a provider, with its response."""
    id: str # UUID
    timestamp: datetime
    system_prompt: str | None
    user_prompt: str
    response: ProviderResponse
    
    