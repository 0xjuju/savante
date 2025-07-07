from app.api.v1.api import api_router
from app.core.config import get_settings
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
