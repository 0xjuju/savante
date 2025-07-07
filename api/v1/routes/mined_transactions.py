from typing import List

from app.core.config import get_redis
from app.schemas.blockchain import MinedTx
from fastapi import APIRouter, Depends, Request
import redis.asyncio as redis

router = APIRouter(prefix="/mined-transactions", tags=["mined_transactions"])
CACHE_PREFIX = "cache:mempool:seen:"


@router.post("")
async def mined_transactions(request: Request, r: redis.Redis = Depends(get_redis)):
    batch: List[MinedTx] = await request.json()

    for tx in batch:
        hash = tx["hash"]

    return {"status": "200"}






