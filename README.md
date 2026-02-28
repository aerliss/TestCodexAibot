# Commercial AI Telegram Bot (aiogram 3.x)

Production-ready starter for a monetized Telegram bot with:
- AI image generation, image editing, video generation.
- Telegram Stars (XTR) payments and credit economy.
- Referral and subscription models.
- Personal cabinet (Telegram WebApp / Mini App) on FastAPI.
- Admin functionality via `/admin` + admin web route.
- Microservices with Redis queue workers and MinIO object storage.

## Stack
- **Bot:** aiogram 3.x
- **Worker:** async queue consumer via Redis
- **DB:** PostgreSQL + SQLAlchemy async
- **Cache/Queue/Sessions:** Redis
- **Object storage:** MinIO
- **WebApp:** FastAPI + Jinja2
- **Retries:** tenacity

## Project structure

- `bot/` – Telegram bot entrypoint and handlers.
- `worker/` – async generation pipeline and providers.
- `webapp/` – Mini App & admin web pages.
- `common/` – shared config, DB, models, storage.
- `scripts/init_db.py` – DB schema bootstrap.

## Deployment & setup

1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Edit required variables in `.env`:
   - `BOT_TOKEN`, `BOT_USERNAME`
   - `GEMINI_API_KEY`
   - `WEBAPP_BASE_URL`
   - pricing (`COST_*`, `PACK_*`, `SUB_*`)
   - `ADMIN_IDS`
3. Build and run:
   ```bash
   docker compose up -d --build
   ```
4. Initialize DB schema:
   ```bash
   docker compose exec bot python scripts/init_db.py
   ```
5. (Optional) scale workers:
   ```bash
   docker compose up -d --scale worker=5
   ```

## Gemini integration notes

Default provider is `gemini` (`PROVIDER=gemini`).
Models are configured with:
- `GEMINI_IMAGE_STANDARD_MODEL=gemini-2.5-flash-image`
- `GEMINI_IMAGE_PRO_MODEL=gemini-3-pro-image-preview`
- `GEMINI_VIDEO_MODEL=veo-3.1-generate-preview`

Provider abstraction supports extending to Stability/Kling/Runway (stubs included).

## WebApp auth in this starter

- `POST /auth/dev/{tg_id}` returns session token and cabinet URL.
- Replace it with real Telegram WebApp initData verification before production.

## Compliance checklist before production

- Implement strict content policy + NSFW moderation.
- Add legal pages (Terms/Privacy/Refunds/GDPR delete endpoint).
- Add backups for Postgres/Redis/MinIO.
- Enable Prometheus/Grafana and bot alerting.

## Tests

```bash
pytest -q
```

