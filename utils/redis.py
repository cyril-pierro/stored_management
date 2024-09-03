from typing import Any

import redis

from config.setting import settings


class Cache:
    _redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        # password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
    )

    @staticmethod
    def set(key: str, value: str, ex=settings.APP_SECRET_KEY_EXPIRES_IN) -> None:
        Cache._redis.set(key, value, ex=ex)

    @staticmethod
    def get(key: str) -> Any:
        value = Cache._redis.get(key)
        return value.decode() if value else None

    @staticmethod
    def delete(key: str) -> None:
        Cache._redis.delete(key)

    @staticmethod
    def incr(key: str) -> None:
        Cache._redis.incr(key)
