from __future__ import annotations

import asyncio

import orjson
from redis.asyncio import Redis

from common.config import get_settings
from worker.app.services.processor import process


async def main() -> None:
    cfg = get_settings()
    redis = Redis.from_url(cfg.redis_url, decode_responses=False)
    while True:
        row = await redis.brpop(cfg.redis_queue_key, timeout=5)
        if not row:
            await asyncio.sleep(0.2)
            continue
        _, raw = row
        await process(redis, orjson.loads(raw))


if __name__ == "__main__":
    asyncio.run(main())
