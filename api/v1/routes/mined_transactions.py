from typing import List

from app.core.config import get_redis
from app.schemas.blockchain import MinedTx
from fastapi import APIRouter, Depends, Request
import redis.asyncio as redis

router = APIRouter(prefix="/blockchain/logs", tags=["logs"])
CACHE_PREFIX = "cache:mempool:seen:"


@router.post("")
async def blockchain_logs(request: Request, r: redis.Redis = Depends(get_redis)):
    data = await request.json()
    chain = data["chain"]

    batch: List[MinedTx] = data["data"]


    if chain == "ethereum":
        bundled: List[MinedTx] = list()  # Transactions that are likely bots
        non_bundled: List[MinedTx] = list()

        for tx in batch:
            tx_hash = tx["transactionHash"]
            key = f"{CACHE_PREFIX}{tx_hash.lower()}"
            if await r.exists(key):
                non_bundled.append(tx)  # Appeared in mempool
            else:
                bundled.append(tx)  # Wasn't seen in mempool cache > likely bot

        res = {
            "mempool_hits": len(non_bundled),
            "bundled": len(bundled),
        }

        print(res)
    else:
        print(f"{len(batch)} transactions on {chain}")

    return {"status": 200}






