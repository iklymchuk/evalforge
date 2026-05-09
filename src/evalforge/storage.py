"""SQLite persistence for prompt runs."""

SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_runs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    system_prompt TEXT,
    response_text TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    raw_response TEXT NOT NULL,
)
"""
    
class RunStore:
    def __init__(self, db_path: str | Path = "evalforge.db"):
        self.db_path = str(db_path)
        with self._conn() as conn:
            conn.executescript(SCHEMA)
            
    def _conn(self):
        return sqlite3.connect(self.db_path)

    def save(self, system_prompt: str | None, user_prompt: str, response: ProviderResponse) -> str:
        run_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO prompt_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    datetime.utcnow().isoformat(),
                    system_prompt,
                    user_prompt,
                    response.provider,
                    response.model, 
                    response.text,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.latency_ms,
                    json.dumps(response.raw),
                )
            )
        return run_id