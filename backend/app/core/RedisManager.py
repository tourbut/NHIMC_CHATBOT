# main.py
from redis.asyncio import Redis, ConnectionPool
from typing import Optional
from .config import settings

class RedisManager:
    _pool: Optional[ConnectionPool] = None
    _redis: Optional[Redis] = None

    @classmethod
    async def get_redis(cls) -> Redis:
        if cls._redis is None:
            cls._pool = ConnectionPool(
                host=settings.REDIS_SERVER,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USER,
                password=settings.REDIS_PASSWORD,
                db=0,
                max_connections=10,
                decode_responses=True
            )
            cls._redis = Redis(connection_pool=cls._pool)
        return cls._redis

    @classmethod
    async def close(cls):
        if cls._redis:
            await cls._redis.close()
            cls._redis = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None