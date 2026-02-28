from __future__ import annotations

import base64
import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from common.config import get_settings
from worker.app.providers.base import Provider

log = logging.getLogger(__name__)
cfg = get_settings()


class GeminiProvider(Provider):
    def __init__(self) -> None:
        self.api_key = cfg.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _call_model(self, model: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/{model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        model = cfg.gemini_image_pro_model if tier == "pro" else cfg.gemini_image_standard_model
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        data = await self._call_model(model, payload)
        images: list[bytes] = []
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData")
                if inline and inline.get("mimeType", "").startswith("image/"):
                    images.append(base64.b64decode(inline["data"]))
        if not images:
            raise RuntimeError("Gemini did not return image content")
        return images

    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        model = cfg.gemini_image_pro_model if tier == "pro" else cfg.gemini_image_standard_model
        parts = [{"text": prompt}]
        for image in inputs[:3]:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(image).decode()}})
        payload = {"contents": [{"parts": parts}]}
        data = await self._call_model(model, payload)
        images: list[bytes] = []
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData")
                if inline and inline.get("mimeType", "").startswith("image/"):
                    images.append(base64.b64decode(inline["data"]))
        if not images:
            raise RuntimeError("Gemini edit API did not return image content")
        return images

    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        model = cfg.gemini_video_model
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        data = await self._call_model(model, payload)
        video_b64 = data.get("video") or data.get("output", {}).get("video")
        if not video_b64:
            log.warning("Video generation API did not return video bytes, using stub.")
            return b"FAKE_MP4"
        return base64.b64decode(video_b64)


class StabilityProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        return [b"STABILITY_STUB_IMAGE"]

    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        return [b"STABILITY_STUB_EDIT"]

    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        return b"STABILITY_STUB_VIDEO"


class RunwayProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        return [b"RUNWAY_STUB_IMAGE"]

    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        return [b"RUNWAY_STUB_EDIT"]

    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        return b"RUNWAY_STUB_VIDEO"


class KlingProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        return [b"KLING_STUB_IMAGE"]

    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        return [b"KLING_STUB_EDIT"]

    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        return b"KLING_STUB_VIDEO"
