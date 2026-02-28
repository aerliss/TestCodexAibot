import orjson
from redis.asyncio import Redis

from common.config import get_settings

cfg = get_settings()


async def enqueue(redis: Redis, payload: dict) -> None:
    await redis.lpush(cfg.redis_queue_key, orjson.dumps(payload))


async def queue_count(redis: Redis, tg_id: int) -> int:
    return int(await redis.get(f"uqueue:{tg_id}") or 0)


async def queue_inc(redis: Redis, tg_id: int) -> None:
    await redis.incr(f"uqueue:{tg_id}")
    await redis.expire(f"uqueue:{tg_id}", 3600)


async def queue_dec(redis: Redis, tg_id: int) -> None:
    value = await redis.decr(f"uqueue:{tg_id}")
    if value <= 0:
        await redis.delete(f"uqueue:{tg_id}")
