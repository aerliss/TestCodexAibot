from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    bot_username: str = Field(alias="BOT_USERNAME")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    minio_endpoint: str = Field(alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(alias="MINIO_BUCKET")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")

    provider: str = Field(default="gemini", alias="PROVIDER")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_image_standard_model: str = Field(alias="GEMINI_IMAGE_STANDARD_MODEL")
    gemini_image_pro_model: str = Field(alias="GEMINI_IMAGE_PRO_MODEL")
    gemini_video_model: str = Field(alias="GEMINI_VIDEO_MODEL")

    free_credits: int = Field(default=5, alias="FREE_CREDITS")
    referral_reward: int = Field(default=10, alias="REFERRAL_REWARD")
    max_user_queue: int = Field(default=5, alias="MAX_USER_QUEUE")

    cost_img_standard: int = Field(default=1, alias="COST_IMG_STANDARD")
    cost_img_pro: int = Field(default=3, alias="COST_IMG_PRO")
    cost_edit_standard: int = Field(default=2, alias="COST_EDIT_STANDARD")
    cost_edit_pro: int = Field(default=4, alias="COST_EDIT_PRO")
    cost_video_standard: int = Field(default=10, alias="COST_VIDEO_STANDARD")
    cost_video_pro: int = Field(default=20, alias="COST_VIDEO_PRO")

    pack_starter_stars: int = Field(default=49, alias="PACK_STARTER_STARS")
    pack_starter_credits: int = Field(default=60, alias="PACK_STARTER_CREDITS")
    pack_pro_stars: int = Field(default=149, alias="PACK_PRO_STARS")
    pack_pro_credits: int = Field(default=220, alias="PACK_PRO_CREDITS")
    sub_monthly_stars: int = Field(default=499, alias="SUB_MONTHLY_STARS")
    sub_annual_stars: int = Field(default=4490, alias="SUB_ANNUAL_STARS")

    redis_queue_key: str = Field(default="jobs:queue", alias="REDIS_QUEUE_KEY")
    redis_result_prefix: str = Field(default="jobs:result:", alias="REDIS_RESULT_PREFIX")

    webapp_base_url: str = Field(alias="WEBAPP_BASE_URL")
    webapp_secret: str = Field(alias="WEBAPP_SECRET")
    session_ttl_seconds: int = Field(default=604800, alias="SESSION_TTL_SECONDS")

    @property
    def admin_id_list(self) -> list[int]:
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
