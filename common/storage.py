from __future__ import annotations

import io
from datetime import timedelta

from minio import Minio

from common.config import get_settings


class MinioStorage:
    def __init__(self) -> None:
        cfg = get_settings()
        self.bucket = cfg.minio_bucket
        self.client = Minio(
            cfg.minio_endpoint,
            access_key=cfg.minio_access_key,
            secret_key=cfg.minio_secret_key,
            secure=cfg.minio_secure,
        )
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_bytes(self, object_name: str, content: bytes, content_type: str) -> str:
        stream = io.BytesIO(content)
        self.client.put_object(self.bucket, object_name, stream, len(content), content_type=content_type)
        return object_name

    def presigned_url(self, object_name: str, expires_hours: int = 24) -> str:
        return self.client.presigned_get_object(
            self.bucket,
            object_name,
            expires=timedelta(hours=expires_hours),
        )
