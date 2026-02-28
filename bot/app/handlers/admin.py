from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from bot.app.services.repository import audit
from common.config import get_settings
from common.db import SessionLocal
from common.models import Job, Payment, User

router = Router()
cfg = get_settings()


@router.message(Command("admin"))
async def admin(message: Message) -> None:
    if message.from_user.id not in cfg.admin_id_list:
        return
    async with SessionLocal() as s:
        users = await s.scalar(select(func.count(User.id)))
        jobs = await s.scalar(select(func.count(Job.id)))
        stars = await s.scalar(select(func.coalesce(func.sum(Payment.stars), 0)).where(Payment.status == "paid"))
    await audit(message.from_user.id, "admin_stats", {})
    await message.answer(f"Пользователи: {users}\nЗадачи: {jobs}\nВыручка XTR: {stars}")
