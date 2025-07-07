from typing import List

from app.schemas.blockchain import MinedTx
from fastapi import APIRouter, Request

router = APIRouter(prefix="/mined-transactions", tags=["mined_transactions"])


@router.post("")
async def mined_transactions(request: Request):
    batch: List[MinedTx] = await request.json()
    print(batch)

    return {"status": "200"}






