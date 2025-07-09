from functools import lru_cache

from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis.asyncio as redis


class Settings(BaseSettings):
    alchemy_api_key: str
    domain: str = "http://127.0.0.1:8000"
    secret_key_middleware: str
    redis_url: str = "redis://localhost:6379"
    build_dataset: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis



