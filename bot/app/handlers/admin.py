from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from bot.app.services.repository import add_audit
from common.config import get_settings
from common.db import SessionLocal
from common.models import Job, Payment, User

router = Router()
cfg = get_settings()


@router.message(Command("admin"))
async def admin_summary(message: Message) -> None:
    if message.from_user.id not in cfg.admin_id_list:
        return
    async with SessionLocal() as session:
        users = await session.scalar(select(func.count(User.id)))
        jobs = await session.scalar(select(func.count(Job.id)))
        paid = await session.scalar(select(func.coalesce(func.sum(Payment.stars), 0)).where(Payment.status == "paid"))
    await add_audit(message.from_user.id, "admin_summary", {})
    await message.answer(f"👮 Admin panel\nUsers: {users}\nJobs: {jobs}\nRevenue (XTR): {paid}")
