from app.services.redis_helper import StreamTools
import pytest
import redis.asyncio as redis


TEST_STREAM = "test:stream"
TEST_PREFIX = "test:tx:"
TEST_MAXLEN = 100
TEST_TTL = 5


@pytest.fixture
async def redis_conn():
    conn = redis.Redis(decode_responses=False)
    await conn.flushdb()
    yield conn
    await conn.flushdb()


@pytest.fixture
def stream_tool(redis_conn):
    return StreamTools(
        stream_name=TEST_STREAM,
        max_length=TEST_MAXLEN,
        cache_prefix=TEST_PREFIX,
        cache_ttl=TEST_TTL,
        redis_conn=redis_conn,
    )
