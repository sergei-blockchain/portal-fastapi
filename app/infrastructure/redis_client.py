from redis import asyncio as aioredis
from app.core.config import settings

class RedisManager:
    def __init__(self):
        self.pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL, 
            decode_responses=True
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        await self.redis.setex(key, ttl, value)

    async def close(self):
        await self.redis.close()

redis_manager = RedisManager()