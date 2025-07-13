from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Generic, TypeVar, Type

import httpx
from pydantic import BaseModel
import redis.asyncio as redis


T = TypeVar("T", bound=BaseModel)


class Batcher(Generic[T]):
    """
    Collects incoming items, flushes them in JSON batches, retries with exponential back-off, and optionally persists
    failed batches.
    """

    def __init__(self, *, name: str, model: Type[T], endpoint: str, chain: str, batch_period: float = 30.0, max_retries: int = 5,
                 redis_prefix: str = "failed:", redis: redis.Redis, http: httpx.AsyncClient):

        self.name = name
        self.model_cls = model
        self.endpoint = endpoint
        self.batch_period = batch_period
        self.max_retries = max_retries
        self.redis_key_pref = f"{redis_prefix}{name}:"

        self.q: asyncio.Queue[T] = asyncio.Queue()
        self.redis = redis
        self.http = http
        self.chain = chain

        self._task = asyncio.create_task(self._flusher())

    async def enqueue(self, item: T | dict) -> None:
        """Add one item (model instance or raw dict) to the queue."""
        if not isinstance(item, self.model_cls):
            item = self.model_cls.model_validate(item)  # parse + type-check
        await self.q.put(item)

    async def close(self):
        """Flush remaining items and cancel flusher"""
        await self._drain_and_send()
        self._task.cancel()

    async def _flusher(self):
        while True:
            await asyncio.sleep(self.batch_period)
            await self._drain_and_send()

    async def _drain_and_send(self):
        batch: list[dict] = []
        while not self.q.empty():
            batch.append(self.q.get_nowait().model_dump(by_alias=True))
        if batch:
            await self._post_with_retry(batch)

    async def _post_with_retry(self, batch: dict[str, list[dict]], attempt: int = 1):
        batch = {
            "chain": self.chain,
            "data": batch
        }
        length = len(batch["data"])
        try:
            r = await self.http.post(self.endpoint, json=batch)
            r.raise_for_status()
            # print(f"sent {length} items OK")
        except Exception as e:
            if attempt > self.max_retries:
                key = f"{self.redis_key_pref}{int(time.time())}:{uuid.uuid4().hex}"
                await self.redis.set(key, json.dumps(batch), ex=86400)
                print(f"stored failed batch {key} ({length} rows) – {e}")
                return
            backoff = 2**attempt
            print(f"retry {attempt} in {backoff} – {e}")
            await asyncio.sleep(backoff)
            await self._post_with_retry(batch, attempt + 1)
