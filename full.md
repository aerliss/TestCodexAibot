# Полная информация по проекту AI Telegram-бота

## 1) Назначение проекта
Проект реализует сервис генерации медиа через Telegram:
- генерация изображений по тексту;
- редактирование изображений;
- генерация видео;
- монетизация через Telegram Stars (XTR) и кредиты;
- личный кабинет пользователя (WebApp);
- базовая админ-функциональность.

Архитектура микросервисная: `bot` + `worker` + `webapp` + `postgres` + `redis` + `minio`.

---

## 2) Общая архитектура

### Сервисы
- **bot**: принимает команды/сообщения Telegram, создает задачи, списывает кредиты, отправляет инвойсы.
- **worker**: асинхронно забирает задачи из Redis-очереди, вызывает AI-провайдер, сохраняет результаты в MinIO.
- **webapp**: личный кабинет и админ-страница, доступ через WebApp-токены и Redis-сессии.
- **postgres**: хранилище пользователей, задач, платежей и журналов.
- **redis**: очередь задач, счетчики лимитов, временные сессии.
- **minio**: объектное хранение результатов генерации (файлы изображений/видео).

### Поток данных
1. Пользователь в Telegram создает задачу.
2. Бот проверяет лимиты/кредиты, создает запись `Job`, кладет задачу в Redis.
3. Worker извлекает задачу, вызывает провайдер, сохраняет файлы в MinIO.
4. Worker обновляет статус задачи в Postgres и освобождает пользовательский слот очереди.
5. WebApp отображает историю задач и ссылки скачивания (presigned URL из MinIO).

---

## 3) Полная сводка по файлам

## Корень проекта
- `.env.example` — пример всех ключевых переменных окружения.
- `Dockerfile` — базовый образ и установка зависимостей Python.
- `docker-compose.yml` — подъем всей инфраструктуры и приложений.
- `requirements.txt` — Python-зависимости.
- `README.md` — краткая инструкция.
- `ПРОЕКТ_ПОЛНАЯ_ИНФОРМАЦИЯ.md` — этот подробный документ.

## `common/`
- `common/config.py` — централизованная конфигурация (pydantic settings), парсинг env-переменных.
- `common/db.py` — async-движок SQLAlchemy и фабрика сессий.
- `common/models.py` — ORM-модели:
  - `User` (баланс, tier, язык, подписка, рефералы);
  - `Job` (тип задачи, параметры, статусы, результаты);
  - `Payment` (инвойсы и статус оплаты);
  - `Referral`, `SubscriptionLog`, `AuditLog`.
- `common/storage.py` — обертка MinIO: загрузка байтов и presigned-ссылки.
- `common/security.py` — подпись/проверка токенов WebApp (`auth` параметр).

## `bot/`
- `bot/main_bot.py` — запуск aiogram polling, подключение роутеров.
- `bot/app/handlers/common.py` — `/start`, язык, приветствие, меню.
- `bot/app/handlers/generation.py` — FSM-флоу генерации, проверка лимитов очереди, списание кредитов, постановка задач.
- `bot/app/handlers/payments.py` — выставление инвойса в XTR, pre-checkout, обработка успешной оплаты.
- `bot/app/handlers/admin.py` — базовая админ-статистика.
- `bot/app/keyboards/main.py` — кнопки меню, включая WebApp-кнопку с подписанным токеном.
- `bot/app/services/repository.py` — операции с БД (пользователи, задачи, платежи, аудит).
  - Важно: `complete_payment` сделан идемпотентным (дубли апдейтов оплаты не начисляют кредиты второй раз).
- `bot/app/services/queue.py` — операции очереди и лимитов в Redis.

## `worker/`
- `worker/main_worker.py` — цикл обработки очереди (`BRPOP`).
- `worker/app/providers/base.py` — абстрактный интерфейс провайдера.
- `worker/app/providers/gemini_media.py` — реализация Gemini + stub-провайдеры Stability/Kling/Runway.
- `worker/app/services/processor.py` — логика обработки задач, запись результатов в MinIO, обновление статуса Job, возврат кредитов при ошибке.

## `webapp/`
- `webapp/main_webapp.py` — FastAPI-приложение:
  - `/auth/dev/{tg_id}` для dev-авторизации;
  - `/cabinet` для личного кабинета;
  - `/admin` для админ-доступа;
  - резолв пользователя через `token` или подписанный `auth`.
- `webapp/app/templates/cabinet.html` — шаблон кабинета.
- `webapp/app/templates/admin.html` — шаблон админ-страницы.
- `webapp/app/static/css/style.css` — минимальные стили.

## `scripts/`
- `scripts/init_db.py` — создание таблиц в БД (bootstrap схемы).

## `tests/`
- `tests/test_config.py` — проверка парсинга конфигурации.
- `tests/test_security.py` — проверка подписи/проверки WebApp токенов.
- `tests/test_payment_idempotency.py` — проверка наличия защиты идемпотентности в обработке оплаты.

---

## 4) Полная сводка по развертке проекта

## Шаг 1. Подготовка
1. Установить Docker и Docker Compose.
2. Клонировать репозиторий.
3. Скопировать env-шаблон:
   ```bash
   cp .env.example .env
   ```
4. Заполнить минимум:
   - `BOT_TOKEN`
   - `BOT_USERNAME`
   - `GEMINI_API_KEY`
   - `WEBAPP_SECRET`
   - при необходимости `ADMIN_IDS`

## Шаг 2. Запуск инфраструктуры и приложений
```bash
docker compose up -d --build
```
Поднимутся:
- Postgres: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `localhost:9000`
- MinIO Console: `localhost:9001`
- WebApp: `localhost:8080`

## Шаг 3. Инициализация схемы БД
```bash
docker compose exec bot python scripts/init_db.py
```

## Шаг 4. Проверка работоспособности
Рекомендуемые проверки:
```bash
docker compose ps
docker compose logs bot --tail=100
docker compose logs worker --tail=100
docker compose logs webapp --tail=100
```

## Шаг 5. Масштабирование worker
Для увеличения throughput очереди:
```bash
docker compose up -d --scale worker=5
```

## Шаг 6. Бэкапы (рекомендуется)
Для production добавить:
- регулярный dump Postgres;
- snapshot/backup Redis (AOF/RDB по политике);
- versioned bucket policy для MinIO.

## Шаг 7. Безопасность и эксплуатация (production checklist)
1. Выключить dev-auth (`/auth/dev/{tg_id}`) и включить валидацию Telegram initData.
2. Настроить HTTPS и reverse proxy (Nginx/Traefik).
3. Ограничить доступ к MinIO Console.
4. Добавить мониторинг (Prometheus/Grafana) и алерты.
5. Добавить ротацию логов и централизованный сбор.
6. Включить контент-модерацию и юридические документы (Terms/Privacy/Refund).

---

## 5) Ключевые конфигурационные параметры

### Telegram и доступ
- `BOT_TOKEN`, `BOT_USERNAME`, `ADMIN_IDS`

### База и кеш
- `DATABASE_URL`, `REDIS_URL`

### Хранилище
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`, `MINIO_SECURE`

### AI-провайдер
- `PROVIDER` (`gemini|stability|kling|runway`)
- `GEMINI_API_KEY`
- `GEMINI_IMAGE_STANDARD_MODEL`
- `GEMINI_IMAGE_PRO_MODEL`
- `GEMINI_VIDEO_MODEL`

### Экономика
- `FREE_CREDITS`, `REFERRAL_REWARD`, `MAX_USER_QUEUE`
- `COST_IMG_STANDARD`, `COST_IMG_PRO`, `COST_EDIT_STANDARD`, `COST_EDIT_PRO`, `COST_VIDEO_STANDARD`, `COST_VIDEO_PRO`
- `PACK_STARTER_STARS`, `PACK_STARTER_CREDITS`, `PACK_PRO_STARS`, `PACK_PRO_CREDITS`
- `SUB_MONTHLY_STARS`, `SUB_ANNUAL_STARS`

### WebApp
- `WEBAPP_BASE_URL`, `WEBAPP_SECRET`, `SESSION_TTL_SECONDS`

---

## 6) Эксплуатационные заметки
- Если Telegram повторно присылает успешную оплату, кредиты не задваиваются (идемпотентность).
- WebApp-кнопка из бота работает через подписанный `auth`, что устраняет ошибку прямого входа.
- Воркеры можно масштабировать горизонтально без изменений кода.

---

## 7) Что желательно доработать перед production
- Полноценная валидация Telegram WebApp initData вместо dev-режима.
- Реальные интеграции (не stub) для Stability/Kling/Runway.
- Миграции Alembic вместо bootstrap create_all.
- Интеграционные тесты с testcontainers (Postgres/Redis/MinIO).
- Модерация контента и расширенный аудит действий администраторов.
