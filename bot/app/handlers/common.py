from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.app.keyboards.main import main_menu
from bot.app.services.repository import get_or_create_user

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    ref_code = parts[1][3:] if len(parts) > 1 and parts[1].startswith("ref") else None
    user = await get_or_create_user(message.from_user.id, message.from_user.username, ref_code)
    await message.answer(
        f"Добро пожаловать! Баланс: <b>{user.credits}</b>\n"
        "⚠️ Используя бота, вы принимаете правила и политику приватности.",
        reply_markup=main_menu(message.from_user.id),
    )


@router.message(Command("lang"))
async def lang(message: Message) -> None:
    await message.answer("Используйте: /lang ru или /lang en")


@router.message(F.text == "🌐 Язык")
async def lang_btn(message: Message) -> None:
    await lang(message)
