from app.schemas.blockchain import MemTx
from fastapi import APIRouter, Request
from typing import List


router = APIRouter(prefix="/mempool", tags=["mempool"])


@router.post("")
async def read_mempool(request: Request):
    """Receive streamed transactions from mempool"""
    batch: List[MemTx] = await request.json()
    print(batch)

    return {"status": "200"}

