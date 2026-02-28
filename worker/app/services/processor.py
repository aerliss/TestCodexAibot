from uuid import uuid4

from redis.asyncio import Redis

from bot.app.services.queue import queue_dec
from bot.app.services.repository import refund_credits, set_job
from common.config import get_settings
from common.storage import MinioStorage
from worker.app.providers.gemini_media import GeminiProvider, KlingProvider, RunwayProvider, StabilityProvider

cfg = get_settings()


def get_provider():
    if cfg.provider == "stability":
        return StabilityProvider()
    if cfg.provider == "kling":
        return KlingProvider()
    if cfg.provider == "runway":
        return RunwayProvider()
    return GeminiProvider()


async def process(redis: Redis, payload: dict) -> None:
    provider = get_provider()
    storage = MinioStorage()
    job_id = payload["job_id"]
    tg_id = payload["tg_id"]
    try:
        if payload["kind"] == "img":
            blobs = await provider.generate_image(payload["prompt"], payload["tier"], payload)
            files = [storage.upload_bytes(f"{job_id}/{uuid4()}.jpg", b, "image/jpeg") for b in blobs]
        elif payload["kind"] == "edit":
            blobs = await provider.edit_image(payload["prompt"], [], payload["tier"], payload)
            files = [storage.upload_bytes(f"{job_id}/{uuid4()}.jpg", b, "image/jpeg") for b in blobs]
        else:
            video = await provider.generate_video(payload["prompt"], [], payload["tier"], payload)
            files = [storage.upload_bytes(f"{job_id}/{uuid4()}.mp4", video, "video/mp4")]
        await set_job(job_id, "done", result_files=files)
        await redis.set(f"{cfg.redis_result_prefix}{job_id}", "done", ex=86400)
    except Exception as exc:  # noqa: BLE001
        await set_job(job_id, "error", error=str(exc))
        await refund_credits(tg_id, payload.get("cost", 0))
    finally:
        await queue_dec(redis, tg_id)
