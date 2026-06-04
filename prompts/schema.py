"""Pydantic schemas for prompt YAML files."""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal
from datetime import date

class PromptVariable(BaseModel):
    """A single variable expected by the prompt."""
    name: str
    type: Literal["string", "integer", "number", "boolean"] = "string"
    required: bool = True
    default: Any = None
    description: str | None = None

class PromptDefaults(BaseModel):
    """Default model and sampling parameters for a prompt."""
    provider: str = "anthropic  "
    model: str | None = None
    temperature: float = 1.0
    max_tokens: int = 1024

class PromptSpec(BaseModel):
    """The full schema of a prompt YAML file."""
    name: str
    version: int = Field(ge=1)
    description: str
    author: str | None = None
    created: date | None = None
    tags: list[str] = Field(default_factory=list)
    defaults: PromptDefaults = Field(default_factory=PromptDefaults)
    system_prompt: str | None = None
    user_prompt: str
    variables: list[PromptVariable] = Field(default_factory=list)