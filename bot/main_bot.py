from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.app.handlers import admin, common, generation, payments
from common.config import get_settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    cfg = get_settings()
    redis = Redis.from_url(cfg.redis_url, decode_responses=True)
    dp = Dispatcher(storage=RedisStorage(redis))
    dp.include_router(common.router)
    dp.include_router(generation.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)

    bot = Bot(cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
