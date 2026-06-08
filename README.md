# evalforge

A CLI tool for evaluating and comparing LLM responses. Run ad-hoc prompts across providers, or manage versioned prompt templates — list them, run them with variables, and compare versions side-by-side.

## What it does

- Runs a prompt against **OpenAI** (`gpt-4o-mini`), **Anthropic** (`claude-haiku-4-5`), and **Together** (`Meta-Llama-3-8B-Instruct-Lite`) simultaneously
- Displays responses, token usage, and latency in a Rich table
- Persists every run to a local SQLite database (`evalforge.db`)
- **Versioned prompt templates** stored as YAML files with Jinja2 variable interpolation
- **List, run, and compare** prompt versions without touching code

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

### Compare providers on an ad-hoc prompt

```bash
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

### List available prompts

```bash
evalforge list-prompts
```

Output:

```
      Available Prompts
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Name                 ┃ Versions ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ haiku_writer         │ v1, v2   │
│ code_reviewer        │ v1       │
│ test_case_generator  │ v1       │
└──────────────────────┴──────────┘
```

### Run a prompt with variables

```bash
# Uses the latest version and the prompt's default provider
evalforge run-prompt haiku_writer --var topic=autumn --var style=melancholic

# Pin to a specific version
evalforge run-prompt haiku_writer --version 1 --var topic=autumn

# Override provider or model
evalforge run-prompt haiku_writer --var topic=autumn --provider openai --model gpt-4o-mini
```

Output:

```
haiku_writer v2 via anthropic/claude-haiku-4-5-20251001
Latency: 1105 ms · Tokens: 312 / 89

Crimson leaves descend,
whisper secrets to cold earth—
silence holds them now.
```

### Compare two versions of the same prompt

```bash
evalforge compare-prompts haiku_writer --v1 1 --v2 2 --var topic=autumn
```

Output:

```
       Prompt Comparison: haiku_writer v1 vs v2
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Version ┃ Response                      ┃ Tokens ┃ Latency  ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ v1      │ Leaves drift and fall...      │ 28/45  │ 843ms    │
│ v2      │ <thinking>...</thinking>...   │ 28/112 │ 1204ms   │
└─────────┴───────────────────────────────┴────────┴──────────┘
```

## Versioned prompt templates

Prompts live under `prompts/<name>/v<N>.yaml`. Each file defines metadata, model defaults, Jinja2 system/user prompt templates, and variable schemas:

```yaml
name: haiku_writer
version: 2
description: "Writes haiku using chain-of-thought reasoning."
author: "iklymchuk"
created: 2026-06-07
tags: [creative-writing, chain-of-thought]

defaults:
  provider: anthropic
  model: claude-haiku-4-5-20251001
  temperature: 0.7
  max_tokens: 512

system_prompt: |
  You are a poet who writes traditional Japanese haiku.
  ...

user_prompt: |
  Write a haiku about {{ topic }}.
  Style: {{ style | default('contemplative') }}

variables:
  - name: topic
    type: string
    required: true
  - name: style
    type: string
    required: false
    default: contemplative
```

Add a new version by creating `prompts/<name>/v<N+1>.yaml`. `list-prompts` and `run-prompt` pick it up automatically — no code changes needed.
