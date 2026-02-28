from __future__ import annotations

import logging
from uuid import uuid4

from redis.asyncio import Redis

from bot.app.services.queue import dec_user_queue
from bot.app.services.repository import refund_credits, update_job_status
from common.config import get_settings
from common.storage import MinioStorage
from worker.app.providers.gemini_media import GeminiProvider, KlingProvider, RunwayProvider, StabilityProvider

cfg = get_settings()
log = logging.getLogger(__name__)


def build_provider():
    if cfg.provider == "stability":
        return StabilityProvider()
    if cfg.provider == "runway":
        return RunwayProvider()
    if cfg.provider == "kling":
        return KlingProvider()
    return GeminiProvider()


async def process_job(redis: Redis, payload: dict) -> None:
    provider = build_provider()
    storage = MinioStorage()

    job_id = payload["job_id"]
    tg_id = payload["tg_id"]
    kind = payload["kind"]
    tier = payload["tier"]
    prompt = payload["prompt"]

    try:
        if kind == "img":
            result = await provider.generate_image(prompt, tier, payload)
            names = [storage.upload_bytes(f"{job_id}/{uuid4()}.jpg", blob, "image/jpeg") for blob in result]
        elif kind == "edit":
            result = await provider.edit_image(prompt, [], tier, payload)
            names = [storage.upload_bytes(f"{job_id}/{uuid4()}.jpg", blob, "image/jpeg") for blob in result]
        else:
            blob = await provider.generate_video(prompt, [], tier, payload)
            names = [storage.upload_bytes(f"{job_id}/{uuid4()}.mp4", blob, "video/mp4")]

        await update_job_status(job_id, "done", result_files=names)
        await redis.set(f"{cfg.redis_result_key_prefix}{job_id}", "done", ex=86400)
    except Exception as exc:  # noqa: BLE001
        log.exception("Failed to process job %s", job_id)
        await update_job_status(job_id, "error", error=str(exc))
        await refund_credits(tg_id, payload.get("cost", 0))
    finally:
        await dec_user_queue(redis, tg_id)
