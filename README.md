Коммерческий Telegram бот на AI (aiogram 3.x)

Готовый стартовый шаблон для монетизированного Telegram бота с:

    Генерацией изображений, редактированием изображений и генерацией видео с помощью ИИ.

    Платежами через Telegram Stars (XTR) и системой кредитов.

    Реферальной программой и моделью подписок.

    Личным кабинетом (Telegram WebApp / Mini App) на FastAPI.

    Функционалом администратора через /admin + веб-маршрут для админки.

    Микросервисной архитектурой с очередями на Redis и объектным хранилищем MinIO.

Стек технологий

    Бот: aiogram 3.x

    Воркер: асинхронный потребитель очереди через Redis

    База данных: PostgreSQL + SQLAlchemy (асинхронный режим)

    Кэш/Очереди/Сессии: Redis

    Объектное хранилище: MinIO

    Веб-приложение: FastAPI + Jinja2

    Повторные попытки: tenacity

Структура проекта

    bot/ – точка входа Telegram бота и обработчики.

    worker/ – асинхронный конвейер генерации и провайдеры.

    webapp/ – Mini App и веб-страницы администратора.

    common/ – общая конфигурация, БД, модели, хранилище.

    scripts/init_db.py – инициализация схемы базы данных.

Развертывание и настройка

    Скопируйте шаблон файла с переменными окружения:
    bash

    cp .env.example .env

    Отредактируйте необходимые переменные в .env:

        BOT_TOKEN, BOT_USERNAME

        GEMINI_API_KEY

        WEBAPP_BASE_URL

        цены (COST_*, PACK_*, SUB_*)

        ADMIN_IDS

    Соберите и запустите:
    bash

    docker compose up -d --build

    Инициализируйте схему базы данных:
    bash

    docker compose exec bot python scripts/init_db.py

    (Опционально) масштабируйте воркеры:
    bash

    docker compose up -d --scale worker=5

Особенности интеграции с Gemini

Провайдер по умолчанию — gemini (PROVIDER=gemini).
Модели настраиваются с помощью:

    GEMINI_IMAGE_STANDARD_MODEL=gemini-2.5-flash-image

    GEMINI_IMAGE_PRO_MODEL=gemini-3-pro-image-preview

    GEMINI_VIDEO_MODEL=veo-3.1-generate-preview

Абстракция провайдера позволяет легко добавить поддержку Stability AI, Kling, Runway (заготовки включены).
Авторизация в WebApp в этом стартовом шаблоне

    POST /auth/dev/{tg_id} возвращает токен сессии и URL личного кабинета.

    Перед продакшеном замените на реальную проверку initData от Telegram WebApp.

Контрольный список для выхода в продакшен

    Внедрить строгую политику контента + модерацию NSFW.

    Добавить юридические страницы (Условия использования, Политика конфиденциальности, Возвраты, GDPR-эндпоинт для удаления данных).

    Настроить резервное копирование Postgres/Redis/MinIO.

    Включить Prometheus/Grafana и оповещения для бота.

Тесты
bash

pytest -q

