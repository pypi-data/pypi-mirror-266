import os
from logging import getLogger
import threading

import redis
import redis.asyncio as async_redis

from . import settings

logger = getLogger(__name__)

__all__ = ['r', 'AsyncRedisLock', 'async_redis']

logger.info(f"Connecting to redis at {settings.REDIS_HOST}")
r = redis.Redis(host=settings.REDIS_HOST, port=6379)

class AsyncRedisLock:
    def __init__(self, lock: async_redis.lock.Lock):
        self.lock = lock

    async def __aenter__(self):
        await self.lock.acquire()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.lock.release()