from fastapi import APIRouter, Request


router = APIRouter(prefix="/mempool", tags=["mempool"])


@router.post("")
async def read_mempool(request: Request):
    """Receive streamed transactions from mempool"""
    payload = await request.json()
    print(payload)
    return {"status": "200"}

