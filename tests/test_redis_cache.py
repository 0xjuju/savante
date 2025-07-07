import asyncio
import uuid
from typing import List

from app.schemas.blockchain import MemTx
from .conftest import TEST_PREFIX, TEST_TTL, TEST_STREAM
import pytest


def random_tx() -> MemTx:
    return MemTx(
        hash=uuid.uuid4().hex,
        **{
            "from": uuid.uuid4().hex[:40],
            "to": uuid.uuid4().hex[:40],
            "input": "0x",
            "gas": "21000",
            "gasPrice": "1_000_000_000",
        },
    )


@pytest.mark.asyncio
async def test_add_batch(stream_tool, redis_conn):
    """Each tx in the batch should hit the stream and receive a cache key with the proper TTL"""
    tx_list: List[MemTx] = [random_tx() for _ in range(5)]

    # Convert to dicts with alias names preserved
    payload = [tx.model_dump(by_alias=True) for tx in tx_list]

    await stream_tool.add_batch(payload)

    # Stream should now contain the same number of entries
    assert await redis_conn.xlen(TEST_STREAM) == len(tx_list)

    # Each tx hash should be in the cache with a positive TTL <= configured TTL
    for tx in tx_list:
        ttl = await redis_conn.ttl(f"{TEST_PREFIX}{tx.hash.lower()}")
        assert 0 < ttl <= TEST_TTL
        # hash_seen() should report "seen"
        assert await stream_tool.hash_seen(tx.hash) is True


@pytest.mark.asyncio
async def test_hash_ttl_expiry(stream_tool):
    tx = random_tx()
    await stream_tool.add_batch([tx.model_dump(by_alias=True)])

    # Immediately after insert the hash must be "seen"
    assert await stream_tool.hash_seen(tx.hash) is True

    # Wait until cache expires
    await asyncio.sleep(TEST_TTL + 1)

    # Now the same hash should be treated as unseen again
    assert await stream_tool.hash_seen(tx.hash) is False
