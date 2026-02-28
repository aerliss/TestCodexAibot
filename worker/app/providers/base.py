from __future__ import annotations

from abc import ABC, abstractmethod


class Provider(ABC):
    @abstractmethod
    async def generate_image(self, prompt: str, tier: str, params: dict) -> list[bytes]:
        raise NotImplementedError

    @abstractmethod
    async def edit_image(self, prompt: str, inputs: list[bytes], tier: str, params: dict) -> list[bytes]:
        raise NotImplementedError

    @abstractmethod
    async def generate_video(self, prompt: str, refs: list[bytes], tier: str, params: dict) -> bytes:
        raise NotImplementedError
