from app.api.v1.api import api_router
from app.core.config import get_settings
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware


settings = get_settings()
app = FastAPI(title="API")


app.add_middleware(SessionMiddleware, secret_key=settings.secret_key_middleware)

app.include_router(api_router, prefix="/api")

