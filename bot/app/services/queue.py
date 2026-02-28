from __future__ import annotations

import orjson
from redis.asyncio import Redis

from common.config import get_settings

settings = get_settings()


async def enqueue_job(redis: Redis, payload: dict) -> None:
    await redis.lpush(settings.redis_queue_key, orjson.dumps(payload))


async def get_user_queue_size(redis: Redis, tg_id: int) -> int:
    key = f"user:queue:{tg_id}"
    return int(await redis.get(key) or 0)


async def inc_user_queue(redis: Redis, tg_id: int) -> int:
    key = f"user:queue:{tg_id}"
    value = await redis.incr(key)
    await redis.expire(key, 3600)
    return int(value)


async def dec_user_queue(redis: Redis, tg_id: int) -> None:
    key = f"user:queue:{tg_id}"
    value = await redis.decr(key)
    if value <= 0:
        await redis.delete(key)
