from app.api.v1.api import api_router
from app.core.config import get_settings
from app.services.blockchain import BlockchainParser
import asyncio
from fastapi import FastAPI
import redis.asyncio as redis
from starlette.middleware.sessions import SessionMiddleware


settings = get_settings()
app = FastAPI(title="API")


app.add_middleware(SessionMiddleware, secret_key=settings.secret_key_middleware)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup():
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)

    parser = BlockchainParser("ethereum")

    app.state.stream_tasks = [
        # start listener for mempool transactions
        asyncio.create_task(
            parser.stream_mempool(redis_client=app.state.redis, to_addresses=parser.ROUTERS + parser.AGGREGATORS),
            name="mempool"
        ),

        # start listener for mined transactions
        asyncio.create_task(
            parser.stream_mined_transactions(redis_client=app.state.redis, to_addresses=parser.ROUTERS + parser.AGGREGATORS),
            name="mined_transactions"
        )
    ]


@app.on_event("shutdown")
async def close_resources():
    for task in app.state.tasks:
        task.cancel()
    for task in app.state.tasks:
        try:
            await task
        except asyncio.CancelledError:
            pass

    await app.state.redis.close()



