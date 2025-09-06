import time, asyncio
from redis.asyncio import Redis

class TokenBucket:
    def __init__(self, redis: Redis, key: str, rps: int, burst: int):
        self.redis = redis
        self.key = f'tb:{key}'
        self.rps = max(1, rps)
        self.burst = max(self.rps, burst)

    async def acquire(self, tokens: int = 1) -> None:
        '''
        get tokens
        '''
        while True:
            now = int(time.time())
            k = f'{self.key}:{now}'
            used = await self.redis.incrby(k, tokens)
            if used == tokens:
                await self.redis.expire(k, 2)
            if used <= self.burst:
                if used > self.rps:
                    await asyncio.sleep(0.1)
                return
            await asyncio.sleep(max(0.0, 1.0 - (time.time() - now)))