from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select

from common.config import get_settings
from common.db import SessionLocal
from common.models import AuditLog, Job, Payment, User

settings = get_settings()


async def get_or_create_user(tg_id: int, username: str | None, ref_code: str | None = None) -> User:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        referred_by = None
        if ref_code:
            referrer = await session.scalar(select(User).where(User.ref_id == ref_code))
            referred_by = referrer.id if referrer else None
        user = User(
            tg_id=tg_id,
            username=username,
            credits=settings.free_credits,
            free_granted=True,
            ref_id=secrets.token_hex(4),
            referred_by=referred_by,
        )
        session.add(user)
        await session.commit()
        return user


async def create_job(tg_id: int, kind: str, tier: str, prompt: str, params: dict, input_files: list[str]) -> Job:
    async with SessionLocal() as session:
        job = Job(tg_id=tg_id, kind=kind, tier=tier, prompt=prompt, params=params, input_files=input_files)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job


async def update_job_status(job_id: str, status: str, result_files: list[str] | None = None, error: str | None = None) -> None:
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job:
            return
        job.status = status
        if result_files is not None:
            job.result_files = result_files
        if error:
            job.error = error
        await session.commit()


async def list_user_jobs(tg_id: int, limit: int = 20) -> list[Job]:
    async with SessionLocal() as session:
        result = await session.scalars(select(Job).where(Job.tg_id == tg_id).order_by(desc(Job.created_at)).limit(limit))
        return list(result)


async def charge_credits(tg_id: int, amount: int) -> bool:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or user.credits < amount:
            return False
        user.credits -= amount
        await session.commit()
        return True


async def refund_credits(tg_id: int, amount: int) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.credits += amount
            await session.commit()


async def add_payment(payload: str, tg_id: int, pack_id: str, stars: int, credits: int) -> None:
    async with SessionLocal() as session:
        payment = Payment(payload=payload, tg_id=tg_id, pack_id=pack_id, stars=stars, credits_added=credits)
        session.add(payment)
        await session.commit()


async def complete_payment(payload: str, charge_id: str) -> None:
    async with SessionLocal() as session:
        payment = await session.scalar(select(Payment).where(Payment.payload == payload))
        if not payment:
            return
        payment.status = "paid"
        payment.telegram_payment_charge_id = charge_id
        user = await session.scalar(select(User).where(User.tg_id == payment.tg_id))
        if user:
            user.credits += payment.credits_added
        await session.commit()


async def set_subscription(tg_id: int, days: int) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return
        now = datetime.now(timezone.utc)
        base = user.subscription_end if user.subscription_end and user.subscription_end > now else now
        user.subscription_end = base + timedelta(days=days)
        await session.commit()


async def add_audit(actor_tg_id: int, action: str, meta: dict) -> None:
    async with SessionLocal() as session:
        session.add(AuditLog(actor_tg_id=actor_tg_id, action=action, meta=meta))
        await session.commit()
