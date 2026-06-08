import pytest
from pathlib import Path
from prompts.template import PromptTemplate, PromptRenderError
from prompts.registry import PromptRegistry, PromptNotFoundError

# --- Unit tests (no API calls) ---


def test_template_renders_with_required_variable(tmp_path):
    yaml_content = """
name: test_prompt
version: 1
description: test
user_prompt: "Hello {{ name }}"
variables:
  - name: name
    type: string
    required: true
"""
    p = tmp_path / "v1.yaml"
    p.write_text(yaml_content)
    t = PromptTemplate.from_yaml(p)
    system, user = t.render(name="World")
    assert user == "Hello World"
    assert system is None


def test_template_raises_on_missing_required_variable(tmp_path):
    yaml_content = """
name: test_prompt
version: 1
description: test
user_prompt: "Hello {{ name }}"
variables:
  - name: name
    required: true
"""
    p = tmp_path / "v1.yaml"
    p.write_text(yaml_content)
    t = PromptTemplate.from_yaml(p)
    with pytest.raises(PromptRenderError, match="Missing required variable: 'name'"):
        t.render()


def test_template_applies_default_for_optional_variable(tmp_path):
    yaml_content = """
name: test_prompt
version: 1
description: test
user_prompt: "Hello {{ greeting }} World"
variables:
  - name: greeting
    required: false
    default: dear
"""
    p = tmp_path / "v1.yaml"
    p.write_text(yaml_content)
    t = PromptTemplate.from_yaml(p)
    _, user = t.render()
    assert user == "Hello dear World"


def test_registry_lists_prompts():
    r = PromptRegistry()
    prompts = r.list_prompts()
    assert "haiku_writer" in prompts
    assert 1 in prompts["haiku_writer"]


def test_registry_raises_on_unknown_prompt():
    r = PromptRegistry()
    with pytest.raises(PromptNotFoundError):
        r.get("does_not_exist")


def test_registry_returns_latest_version_by_default():
    r = PromptRegistry()
    t = r.get("haiku_writer")
    assert t.spec.version == 2  # we wrote v2 today


# --- Integration test (hits real API) ---


@pytest.mark.integration
def test_haiku_writer_runs_end_to_end():
    from evalforge.providers.anthropic import AnthropicProvider

    r = PromptRegistry()
    t = r.get("haiku_writer")
    system, user = t.render(topic="testing")
    p = AnthropicProvider()
    response = p.complete(user_prompt=user, system_prompt=system, max_tokens=100)
    assert response.text
    assert response.usage.output_tokens > 0
