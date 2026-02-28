# AI Telegram Bot (пересобранный проект)

## Что внутри
- `bot` (aiogram 3.x)
- `worker` (Redis queue consumer)
- `webapp` (FastAPI mini app)
- `postgres`, `redis`, `minio` через docker compose

## Важные исправления
1. Идемпотентность платежей: повторные `successful_payment` больше не начисляют кредиты повторно.
2. Кнопка «Личный кабинет» теперь открывает WebApp с подписанным auth-параметром, поэтому 401 при прямом входе из Telegram устранён.

## Запуск
```bash
cp .env.example .env
# заполните BOT_TOKEN, BOT_USERNAME, GEMINI_API_KEY, WEBAPP_SECRET
docker compose up -d --build
docker compose exec bot python scripts/init_db.py
```

## Масштабирование
```bash
docker compose up -d --scale worker=5
```
