from __future__ import annotations

import asyncio
import logging

import orjson
from redis.asyncio import Redis

from common.config import get_settings
from worker.app.services.processor import process_job


async def main() -> None:
    cfg = get_settings()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    redis = Redis.from_url(cfg.redis_url, decode_responses=False)

    while True:
        item = await redis.brpop(cfg.redis_queue_key, timeout=5)
        if not item:
            await asyncio.sleep(0.3)
            continue
        _, raw = item
        payload = orjson.loads(raw)
        await process_job(redis, payload)


if __name__ == "__main__":
    asyncio.run(main())
