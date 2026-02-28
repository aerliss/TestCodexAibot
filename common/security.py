from __future__ import annotations

from itsdangerous import BadSignature, URLSafeSerializer

from common.config import get_settings


class WebAppSigner:
    def __init__(self) -> None:
        cfg = get_settings()
        self.serializer = URLSafeSerializer(cfg.webapp_secret, salt="cabinet-auth")

    def sign_tg_id(self, tg_id: int) -> str:
        return self.serializer.dumps({"tg_id": tg_id})

    def verify(self, token: str) -> int | None:
        try:
            data = self.serializer.loads(token)
            return int(data.get("tg_id"))
        except (BadSignature, ValueError, TypeError):
            return None
