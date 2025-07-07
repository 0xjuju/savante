from __future__ import annotations
import orjson
import time
from typing import Iterable


from app.core.config import get_settings
import redis.asyncio as redis


settings = get_settings()


class StreamTools:

    def __init__(
        self,
        stream_name: str,
        max_length: int,
        cache_prefix: str,
        cache_ttl: int,
        redis_conn: redis.Redis,
    ):
        self.stream = stream_name
        self.max_length = max_length
        self.cache_px = cache_prefix
        self.cache_ttl = cache_ttl
        self.redis = redis_conn

    async def add_batch(self, txs: Iterable[dict]) -> None:
        """Add each transaction to redis stream and set TTL for each one"""
        now = int(time.time() * 1000)
        async with self.redis.pipeline(transaction=False) as pipe:
            for tx in txs:
                data: bytes = orjson.dumps(tx)
                await pipe.xadd(
                    self.stream,
                    {"data": data},
                    maxlen=self.max_length,
                    approximate=True,
                )
                await pipe.setex(f"{self.cache_px}{tx['hash'].lower()}", self.cache_ttl, 1)
            await pipe.execute()

    async def hash_seen(self, tx_hash: str) -> bool:
        """
        Public mempool lookup: True if we saw the hash in the last TTL window
        """
        return await self.redis.exists(f"{self.cache_px}{tx_hash.lower()}") == 1


def get_stream_tools(connection, stream_name: str, *, maxlen: int = 100_000, cache_prefix: str, cache_ttl: int = 120
                     ) -> StreamTools:
    """Factory for StreamTools"""
    return StreamTools(stream_name, maxlen, cache_prefix, cache_ttl, connection)
