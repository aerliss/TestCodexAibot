from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from redis.asyncio import Redis

from bot.app.services.queue import enqueue, queue_count, queue_inc
from bot.app.services.repository import charge_credits, create_job, get_or_create_user
from common.config import get_settings

cfg = get_settings()
router = Router()


class CreateStates(StatesGroup):
    waiting_prompt = State()


@router.message(F.text.in_({"🖼 Генерация", "🎬 Видео", "🛠 Редактирование"}))
async def select_kind(message: Message, state: FSMContext) -> None:
    kind = {"🖼 Генерация": "img", "🎬 Видео": "video", "🛠 Редактирование": "edit"}[message.text]
    await state.update_data(kind=kind)
    await state.set_state(CreateStates.waiting_prompt)
    await message.answer("Введите промпт (можно добавить параметры через ';').")


@router.message(CreateStates.waiting_prompt)
async def accept_prompt(message: Message, state: FSMContext) -> None:
    redis = Redis.from_url(cfg.redis_url, decode_responses=False)
    if await queue_count(redis, message.from_user.id) >= cfg.max_user_queue:
        await message.answer("Лимит задач в очереди достигнут.")
        return

    data = await state.get_data()
    kind = data["kind"]
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    cost = {
        ("img", "standard"): cfg.cost_img_standard,
        ("img", "pro"): cfg.cost_img_pro,
        ("edit", "standard"): cfg.cost_edit_standard,
        ("edit", "pro"): cfg.cost_edit_pro,
        ("video", "standard"): cfg.cost_video_standard,
        ("video", "pro"): cfg.cost_video_pro,
    }[(kind, user.tier)]

    if not await charge_credits(message.from_user.id, cost):
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить starter", callback_data="buy_starter")]])
        await message.answer("Недостаточно кредитов, купите пакет.", reply_markup=kb)
        return

    job = await create_job(message.from_user.id, kind, user.tier, message.text, {"raw": message.text}, [])
    await queue_inc(redis, message.from_user.id)
    await enqueue(
        redis,
        {
            "job_id": str(job.id),
            "tg_id": message.from_user.id,
            "kind": kind,
            "tier": user.tier,
            "prompt": message.text,
            "cost": cost,
        },
    )
    await state.clear()
    await message.answer(f"Задача {job.id} поставлена в очередь")
