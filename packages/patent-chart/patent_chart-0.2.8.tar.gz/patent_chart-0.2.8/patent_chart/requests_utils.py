import os
import asyncio
import time
from typing import Optional
from abc import ABC, abstractmethod

from patent_chart import settings
from patent_chart.redis_utils import r, AsyncRedisLock, async_redis

TTL_KEY_DOESNT_EXIST = -2

Lock = asyncio.Lock | AsyncRedisLock

class FixedWindowRateLimiterBase(ABC):
    def __init__(self, capacity: int, fill_interval: float | int, lock: Lock):
        self.capacity = capacity
        self.fill_interval = fill_interval
        self.lock = lock

    @property
    @abstractmethod
    def tokens(self):
        pass
    
    @tokens.setter
    @abstractmethod
    def tokens(self, value):
        pass

    @property
    @abstractmethod
    def last_fill_time(self):
        pass

    @last_fill_time.setter
    @abstractmethod
    def last_fill_time(self, value):
        pass

    def close(self):
        self.refill_task.cancel()

    async def remove_tokens(self, n: int):
        async with self.lock:
            self.tokens -= n
    
    async def request_and_remove_tokens(self, n: int):
        async with self.lock:
            if self.tokens >= n:
                self.tokens -= n
                return True
            else:
                return False
            
    async def wait_for_tokens(self, n: int, timeout: int = 3600):
        if n > self.capacity:
            raise ValueError(f"n tokens {n} must be less than or equal to capacity {self.capacity}")
        start_time = time.monotonic()
        while True:
            if await self.request_and_remove_tokens(n):
                return True
            if time.monotonic() - start_time > timeout:
                return False
            await asyncio.sleep(self.fill_interval - (time.monotonic() - self.last_fill_time))

    async def fill_tokens(self):
        async with self.lock:
            self.tokens = self.capacity
            self.last_fill_time = time.monotonic()

    async def refill(self):
        while True:
            await self.fill_tokens()
            await asyncio.sleep(self.fill_interval)

    async def __aenter__(self):
        self.refill_task = asyncio.create_task(self.refill())
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

class FixedWindowRateLimiter(FixedWindowRateLimiterBase):
    def __init__(self, capacity: int, fill_interval: float):
        super().__init__(capacity, fill_interval, asyncio.Lock())

    @property
    def last_fill_time(self):
        return self._last_fill_time
    
    @last_fill_time.setter
    def last_fill_time(self, value):
        self._last_fill_time = value

    @property
    def tokens(self):
        return self._tokens
    
    @tokens.setter
    def tokens(self, value):
        self._tokens = value
    

class DistributedFixedWindowRateLimiter(FixedWindowRateLimiterBase):
    def __init__(self, capacity: int, fill_interval: int):
        assert fill_interval > 0, "fill_interval must be greater than 0"
        self.async_r = async_redis.Redis(host=settings.REDIS_HOST, port=6379)
        openai_rate_limit_lock = async_redis.lock.Lock(self.async_r, settings.REDIS_OPENAI_RATE_LIMIT_LOCK_KEY, timeout=3600)
        super().__init__(capacity, fill_interval, AsyncRedisLock(openai_rate_limit_lock))
        
    @property
    def last_fill_time(self):
        last_fill_time = r.get(settings.REDIS_OPENAI_RATE_LIMIT_LAST_FILL_TIME_KEY)
        if last_fill_time is None:
            return -1
        return float(last_fill_time)
    
    @last_fill_time.setter
    def last_fill_time(self, value):
        exp = int(self.fill_interval * 2)
        r.setex(settings.REDIS_OPENAI_RATE_LIMIT_LAST_FILL_TIME_KEY, exp, value)

    @property
    def tokens(self):
        tokens = r.get(settings.REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY)
        if tokens is None:
            return 0
        return int(tokens)
    
    @tokens.setter
    def tokens(self, value):
        ttl = r.ttl(settings.REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY)
        if ttl <= 0:
            ttl = self.fill_interval
        r.setex(settings.REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY, ttl, value)

    async def fill_tokens(self):
        async with self.lock:
            tokens_ttl = r.ttl(settings.REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY)
            if tokens_ttl == TTL_KEY_DOESNT_EXIST:
                try:
                    result = await self.async_r.setex(settings.REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY, self.fill_interval, self.capacity)
                except Exception as e:
                    print(e)
                self.last_fill_time = time.monotonic()

    async def refill(self):
        while True:
            await self.fill_tokens()
            # sleep for the remaining time in the fill interval + 1 second, then whichever process wakes up first will refill the tokens
            sleep_for = self.fill_interval - (time.monotonic() - self.last_fill_time) + 1
            await asyncio.sleep(sleep_for)

    async def __aexit__(self, exc_type, exc_value, traceback):
        super().close()
        await self.async_r.aclose()
        return False