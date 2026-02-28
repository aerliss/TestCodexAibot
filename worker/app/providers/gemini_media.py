from __future__ import annotations

import base64

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from common.config import get_settings
from worker.app.providers.base import Provider

cfg = get_settings()


class GeminiProvider(Provider):
    def __init__(self) -> None:
        self.api_key = cfg.gemini_api_key
        self.base = "https://generativelanguage.googleapis.com/v1beta/models"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _req(self, model: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.base}/{model}:generateContent", params={"key": self.api_key}, json=payload)
            r.raise_for_status()
            return r.json()

    @staticmethod
    def _extract_images(data: dict) -> list[bytes]:
        out = []
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData")
                if inline and inline.get("mimeType", "").startswith("image/"):
                    out.append(base64.b64decode(inline["data"]))
        if not out:
            raise RuntimeError("no image bytes returned")
        return out

    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        model = cfg.gemini_image_pro_model if tier == "pro" else cfg.gemini_image_standard_model
        data = await self._req(model, {"contents": [{"parts": [{"text": prompt}]}]})
        return self._extract_images(data)

    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        model = cfg.gemini_image_pro_model if tier == "pro" else cfg.gemini_image_standard_model
        parts = [{"text": prompt}]
        for image in inputs[:3]:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(image).decode()}})
        data = await self._req(model, {"contents": [{"parts": parts}]})
        return self._extract_images(data)

    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        data = await self._req(cfg.gemini_video_model, {"contents": [{"parts": [{"text": prompt}]}]})
        encoded = data.get("video") or data.get("output", {}).get("video")
        return base64.b64decode(encoded) if encoded else b"FAKE_MP4"


class StabilityProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]: return [b"STABILITY_IMG"]
    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]: return [b"STABILITY_EDIT"]
    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes: return b"STABILITY_VIDEO"


class KlingProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]: return [b"KLING_IMG"]
    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]: return [b"KLING_EDIT"]
    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes: return b"KLING_VIDEO"


class RunwayProvider(Provider):
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]: return [b"RUNWAY_IMG"]
    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]: return [b"RUNWAY_EDIT"]
    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes: return b"RUNWAY_VIDEO"
