# evalforge

A CLI tool for comparing LLM responses across providers side-by-side. Send one prompt, get results from OpenAI, Anthropic, and Together in a single table with response text, token counts, and latency.

## What it does

- Runs a prompt against **OpenAI** (`gpt-4o-mini`), **Anthropic** (`claude-haiku-4-5`), and **Together** (`Meta-Llama-3-8B-Instruct-Lite`) simultaneously
- Displays responses, token usage, and latency in a Rich table
- Persists every run to a local SQLite database (`evalforge.db`)

## Install

Requires Python 3.11+.

```bash
git clone https://github.com/iklymchuk/evalforge.git
cd evalforge
python -m venv venv && source venv/bin/activate
pip install -e .
```

Copy your API keys into a `.env` file at the project root:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TOGETHER_API_KEY=...
```

## Usage

```bash
# Basic comparison
evalforge compare "Explain recursion in one sentence."

# With a system prompt
evalforge compare "Write a haiku about software testing." \
  --system "You are a poetic assistant."
```

Output:

```
                        Model Comparison
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Provider  ┃ Model                   ┃ Response       ┃ Tokens (in/out) ┃ Latency (ms) ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ openai    │ gpt-4o-mini             │ Code breaks... │ 30 / 40         │ 823          │
│ anthropic │ claude-haiku-4-5-...    │ Tests run...   │ 22 / 27         │ 1241         │
│ together  │ meta-llama/Meta-Llama.. │ Bugs hide...   │ 28 / 35         │ 654          │
└───────────┴─────────────────────────┴────────────────┴─────────────────┴──────────────┘
```