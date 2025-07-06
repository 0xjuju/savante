from fastapi import APIRouter
from .routes import mempool


api_router = APIRouter()

api_router.include_router(mempool.router)


