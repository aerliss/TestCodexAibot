from common.config import Settings


def test_admin_ids_parse():
    s = Settings(
        BOT_TOKEN="x",
        BOT_USERNAME="b",
        ADMIN_IDS="1,2,3",
        DATABASE_URL="postgresql+asyncpg://u:p@localhost/db",
        REDIS_URL="redis://localhost:6379/0",
        MINIO_ENDPOINT="localhost:9000",
        MINIO_ACCESS_KEY="a",
        MINIO_SECRET_KEY="b",
        MINIO_BUCKET="media",
        GEMINI_IMAGE_STANDARD_MODEL="m1",
        GEMINI_IMAGE_PRO_MODEL="m2",
        GEMINI_VIDEO_MODEL="m3",
        WEBAPP_BASE_URL="http://localhost",
        WEBAPP_SECRET="secret",
    )
    assert s.admin_id_list == [1, 2, 3]
