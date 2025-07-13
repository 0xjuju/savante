from app.schemas.blockchain import MemTx
from app.services.redis_helper import get_stream_tools
from fastapi import APIRouter, Request
from typing import List


router = APIRouter(prefix="/mempool", tags=["mempool"])


@router.post("")
async def read_mempool(request: Request):
    """Receive streamed transactions from mempool"""

    stream_tools = get_stream_tools(
        stream_name="stream:mempool",
        cache_prefix="cache:mempool:seen:",
        maxlen=100_000,
        cache_ttl=120,
        connection=request.app.state.redis
    )
    data = await request.json()
    batch: List[MemTx] = data["data"]
    await stream_tools.add_batch(batch)

    return {"processed": len(batch)}

