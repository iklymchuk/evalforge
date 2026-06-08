"""SQLite persistence for prompt runs."""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from evalforge.models import ProviderResponse

SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_runs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    prompt_name TEXT,
    prompt_version INTEGER,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    system_prompt TEXT,
    response_text TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    raw_response TEXT NOT NULL
)
"""

# Lightweight migration for existing databases
MIGRATIONS = [
    "ALTER TABLE prompt_runs ADD COLUMN prompt_name TEXT;",
    "ALTER TABLE prompt_runs ADD COLUMN prompt_version INTEGER;",
]


class RunStore:
    def __init__(self, db_path: str | Path = "evalforge.db"):
        self.db_path = str(db_path)
        with self._conn() as conn:
            conn.executescript(SCHEMA)
            # Apply migrations idempotently
            for migration in MIGRATIONS:
                try:
                    conn.execute(migration)
                except sqlite3.OperationalError:
                    pass  # column already exists

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def save(
        self, system_prompt: str | None, user_prompt: str, response: ProviderResponse
    ) -> str:
        run_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO prompt_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    datetime.utcnow().isoformat(),
                    response.provider,
                    response.model,
                    user_prompt,
                    system_prompt,
                    response.text,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.latency_ms,
                    json.dumps(response.raw),
                ),
            )
        return run_id

    def save_prompt_run(
        self,
        prompt_name: str,
        prompt_version: int,
        system_prompt: str | None,
        user_prompt: str,
        response: "ProviderResponse",
    ) -> str:
        run_id = str(uuid.uuid4())
        with self._conn() as c:
            c.execute(
                """INSERT INTO prompt_runs
                   (id, timestamp, prompt_name, prompt_version, system_prompt, user_prompt,
                    provider, model, response_text, input_tokens, output_tokens,
                    latency_ms, raw_response)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    datetime.utcnow().isoformat(),
                    prompt_name,
                    prompt_version,
                    system_prompt,
                    user_prompt,
                    response.provider,
                    response.model,
                    response.text,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.latency_ms,
                    json.dumps(response.raw),
                ),
            )
        return run_id
