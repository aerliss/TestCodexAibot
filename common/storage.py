from datetime import timedelta
from io import BytesIO

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

    def upload_bytes(self, object_name: str, blob: bytes, content_type: str) -> str:
        self.client.put_object(self.bucket, object_name, BytesIO(blob), len(blob), content_type=content_type)
        return object_name

    def url(self, object_name: str, hours: int = 24) -> str:
        return self.client.presigned_get_object(self.bucket, object_name, expires=timedelta(hours=hours))
