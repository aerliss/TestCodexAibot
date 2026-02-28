from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.app.keyboards.main import main_menu
from bot.app.services.repository import get_or_create_user

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    ref_code = None
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("ref"):
        ref_code = parts[1][3:]
    user = await get_or_create_user(message.from_user.id, message.from_user.username, ref_code)
    disclaimer = (
        "⚠️ Используя бота, вы принимаете Terms/Privacy. "
        "Запрещен NSFW/нелегальный контент. Запросы могут модерироваться."
    )
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Ваш баланс: <b>{user.credits}</b> кредитов.\n{disclaimer}",
        reply_markup=main_menu(),
    )


@router.message(F.text == "🌐 Язык")
async def change_lang(message: Message) -> None:
    await message.answer("Доступные языки: ru/en. Команда: /lang ru или /lang en")
