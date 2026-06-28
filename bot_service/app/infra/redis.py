import redis.asyncio as aioredis
from app.core.config import settings


def get_redis() -> aioredis.Redis:
    """
    Возвращает асинхронный Redis-клиент.
    Создаётся один раз и переиспользуется.
    """
    return aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )