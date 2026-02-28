from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from redis.asyncio import Redis

from bot.app.services.queue import enqueue_job, get_user_queue_size, inc_user_queue
from bot.app.services.repository import charge_credits, create_job, get_or_create_user
from common.config import get_settings

router = Router()
settings = get_settings()


class GenStates(StatesGroup):
    choose_kind = State()
    wait_prompt = State()


@router.message(F.text.in_({"🖼 Генерация", "🎬 Видео", "🛠 Редактирование"}))
async def ask_prompt(message: Message, state: FSMContext) -> None:
    kind_map = {"🖼 Генерация": "img", "🎬 Видео": "video", "🛠 Редактирование": "edit"}
    await state.update_data(kind=kind_map[message.text])
    await state.set_state(GenStates.wait_prompt)
    await message.answer("Введите промпт и параметры (например: style=cinematic; ratio=16:9)")


@router.message(GenStates.wait_prompt)
async def create_job_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    kind = data["kind"]
    redis = Redis.from_url(settings.redis_url, decode_responses=False)

    queued = await get_user_queue_size(redis, message.from_user.id)
    if queued >= settings.max_user_queue:
        await message.answer("Лимит очереди: максимум 5 задач. Дождитесь завершения.")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    tier = user.tier
    cost_map = {
        ("img", "standard"): settings.cost_img_standard,
        ("img", "pro"): settings.cost_img_pro,
        ("edit", "standard"): settings.cost_edit_standard,
        ("edit", "pro"): settings.cost_edit_pro,
        ("video", "standard"): settings.cost_video_standard,
        ("video", "pro"): settings.cost_video_pro,
    }
    cost = cost_map[(kind, tier)]
    if not await charge_credits(message.from_user.id, cost):
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Купить кредиты", callback_data="buy_starter")]]
        )
        await message.answer("Недостаточно кредитов. Автопокупка пакета доступна ниже.", reply_markup=kb)
        return

    job = await create_job(
        tg_id=message.from_user.id,
        kind=kind,
        tier=tier,
        prompt=message.text,
        params={"raw": message.text},
        input_files=[],
    )
    await inc_user_queue(redis, message.from_user.id)
    await enqueue_job(
        redis,
        {
            "job_id": str(job.id),
            "tg_id": message.from_user.id,
            "kind": kind,
            "tier": tier,
            "prompt": message.text,
            "cost": cost,
        },
    )
    await state.clear()
    await message.answer(f"Задача {job.id} добавлена в очередь.")
