from fastapi import APIRouter
from .routes import mempool
from .routes import mined_transactions


api_router = APIRouter()

api_router.include_router(mempool.router)
api_router.include_router(mined_transactions.router)


