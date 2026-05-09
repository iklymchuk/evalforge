"""evalforce cli"""

import click
from rich.console import Console
from rich.table import Table
from evalforge.providers.openai import OpenAIProvider
from evalforge.providers.anthropic import AnthropicProvider
from evalforge.providers.together import TogetherProvider
from evalforge.storage import RunStore

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