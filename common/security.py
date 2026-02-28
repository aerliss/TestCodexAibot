from itsdangerous import BadSignature, URLSafeSerializer

from common.config import get_settings


class WebAppSigner:
    def __init__(self) -> None:
        cfg = get_settings()
        self.serializer = URLSafeSerializer(cfg.webapp_secret, salt="cabinet-auth")

    def issue(self, tg_id: int) -> str:
        return self.serializer.dumps({"tg_id": tg_id})

    def parse(self, token: str) -> int | None:
        try:
            return int(self.serializer.loads(token).get("tg_id"))
        except (BadSignature, ValueError, TypeError):
            return None
