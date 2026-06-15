"""Concurrent batch execution of LLM calls."""

import asyncio
import uuid
from evalforge.models import BatchJob, BatchResult, JobResult
from evalforge.providers.base import Provider

class ParallelRunner:
    def __init__(self, providers: dict[str, Provider], concurrency: int = 5):
        self._providers = providers
        self._concurrency = concurrency

    async def _run_one(self, job: BatchJob, sem: asyncio.Semaphore) -> JobResult:
        provider = self._providers[job.provider]

        async with sem:
            try:
                response = await provider.async_complete(
                    user_prompt=job.user_prompt,
                    system_prompt=job.system_prompt,
                    model=job.model,
                    max_tokens=job.max_tokens,
                    temperature=job.temperature,
                )
                return JobResult(job=job, response=response)
            except Exception as e:
                return JobResult(job=job, error=f"{type(e).__name__}: {e}")

    async def run(self, jobs: list[BatchJob]) -> BatchResult:
        sem = asyncio.Semaphore(self._concurrency)
        tasks = [self._run_one(job, sem) for job in jobs]
        results = await asyncio.gather(*tasks)
        return BatchResult(batch_id=str(uuid.uuid4()), results=results)
        
        
        
        
        