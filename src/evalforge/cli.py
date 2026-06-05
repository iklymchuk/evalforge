"""evalforce cli"""

import sys
from pathlib import Path

# prompts/ lives at the project root, not under src/
sys.path.insert(0, str(Path(__file__).parents[2]))

import click
from rich.console import Console
from rich.table import Table
from evalforge.providers.openai import OpenAIProvider
from evalforge.providers.anthropic import AnthropicProvider
from evalforge.providers.together import TogetherProvider
from evalforge.storage import RunStore
from prompts.registry import PromptRegistry, PromptNotFoundError
from prompts.template import PromptRenderError

PROVIDERS = {
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "together": TogetherProvider(),
}

console = Console()


@click.group()
def main():
    """evalforge: evaluate LLM applications"""


@main.command()
@click.argument("prompt")
@click.option("--system", default=None, help="System prompt.")
def compare(prompt: str, system: str | None):
    """Run PROMPT against all configured providers and show results."""
    providers = [OpenAIProvider(), AnthropicProvider(), TogetherProvider()]
    store = RunStore()

    table = Table(title="Model Comparation")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Response", overflow="fold")
    table.add_column("Tokens (in/out)")
    table.add_column("Latency (ms)")

    for provider in providers:
        try:
            response = provider.complete(prompt, system_prompt=system)
            store.save(system, prompt, response)
            table.add_row(
                response.provider,
                response.model,
                response.text[:200] + "..." if len(response.text) > 200 else "",
                f"{response.usage.input_tokens} / {response.usage.output_tokens}",
                str(response.latency_ms),
            )
        except Exception as e:
            table.add_row(provider.name, "-", f"[red]ERROR: {e}[/red]", "-", "-")
    console.print(table)


@main.command(name="list-prompts")
def list_prompts():
    """List all available prompts and their versions."""
    registry = PromptRegistry()
    prompts = registry.list_prompts()
    if not prompts:
        console.print("[yellow]No prompts found in ./prompts/[/yellow]")
        return
    table = Table(title="Available Prompts")
    table.add_column("Name")
    table.add_column("Versions")
    for name, versions in prompts.items():
        table.add_row(name, ", ".join(f"v{v}" for v in versions))
    console.print(table)


@main.command(name="run-prompt")
@click.argument("name")
@click.option(
    "--version", type=int, default=None, help="Specific version (default: latest)."
)
@click.option(
    "--var", "variables", multiple=True, help="Variable as key=value. Repeatable."
)
@click.option(
    "--provider", type=str, default=None, help="Override the prompt's default provider."
)
@click.option("--model", default=None, help="Override the prompt's default model.")
def run_prompt(
    name: str,
    version: int | None,
    variables: tuple[str, ...],
    provider: str | None,
    model: str | None,
):
    """Run a stored prompt by name, optionally at the specific --version."""
    registry = PromptRegistry()
    try:
        template = registry.get(name, version)
    except PromptNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        return

    var_dict = {}
    for v in variables:
        if "=" not in v:
            console.print(f"[red]Invalid --var: {v}. Expected key=value[/red]")
            return
        k, val = v.split("=", 1)
        var_dict[k.strip()] = val.strip()

    try:
        system_prompt, user_prompt = template.render(**var_dict)
    except PromptRenderError as e:
        console.print(f"[red]Render error: {e}[/red]")
        return

    provider_name = provider or template.spec.defaults.provider
    provider_instance = PROVIDERS.get(provider_name)
    if not provider_instance:
        console.print(f"[red]Unknown provider: {provider_name}[/red]")
        return

    response = provider_instance.complete(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model=model or template.spec.defaults.model,
        max_tokens=template.spec.defaults.max_tokens,
        temperature=template.spec.defaults.temperature,
    )

    store = RunStore()
    store.save_prompt_run(
        prompt_name=template.spec.name,
        prompt_version=template.spec.version,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response=response,
    )
    console.print(
        f"\n[bold cyan]{name} v{template.spec.version}[/bold cyan] via {response.provider}/{response.model}"
    )
    console.print(
        f"[dim]Latency: {response.latency_ms} ms · Tokens: {response.usage.input_tokens} / {response.usage.output_tokens}[/dim]\n"
    )
    console.print(response.text)
