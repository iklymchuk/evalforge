"""Renderable prompt template, loaded from YAML spec."""

from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError
from .schema import PromptSpec
import yaml


class PromptRenderError(Exception):
    """Raised when prompt rendering fails."""


class PromptTemplate:
    """A loaded, validated, renderable prompt"""

    def __init__(self, spec: PromptSpec):
        self.spec = spec
        self._env = Environment(undefined=StrictUndefined)
        self._user_template = self._env.from_string(spec.user_prompt)
        self._system_template = (
            self._env.from_string(spec.system_prompt) if spec.system_prompt else None
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "PromptTemplate":
        path = Path(path)
        with path.open() as f:
            data = yaml.safe_load(f)
            spec = PromptSpec.model_validate(data)
        return cls(spec)

    def render(self, **variables: Any) -> tuple[str | None, str]:
        """Render system_prompt and user_prompt with the given variables.

        Returns (system_prompt_rendered, user_prompt_rendered).
        Raises PromptRenderError on missing required variables.
        """

        # Apply defaults for optional variables not provided
        ctx = dict(variables)
        for var in self.spec.variables:
            if var.name not in ctx:
                if var.required:
                    raise PromptRenderError(f"Missing required variable: {var.name!r}")
                if var.default is not None:
                    ctx[var.name] = var.default
        try:
            user = self._user_template.render(**ctx)
            system = (
                self._system_template.render(**ctx) if self._system_template else None
            )
        except TemplateError as e:
            raise PromptRenderError(f"Render failed: {e}") from e

        return system, user
