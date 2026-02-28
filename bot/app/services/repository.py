from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select

from common.config import get_settings
from common.db import SessionLocal
from common.models import AuditLog, Job, Payment, Referral, User

cfg = get_settings()


async def get_or_create_user(tg_id: int, username: str | None, ref_code: str | None = None) -> User:
    async with SessionLocal() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user

        referred_by = None
        if ref_code:
            referrer = await s.scalar(select(User).where(User.ref_id == ref_code))
            if referrer:
                referred_by = referrer.tg_id
                referrer.credits += cfg.referral_reward
                s.add(Referral(referrer_tg_id=referrer.tg_id, referred_tg_id=tg_id, reward_credits=cfg.referral_reward))

        user = User(
            tg_id=tg_id,
            username=username,
            credits=cfg.free_credits,
            free_granted=True,
            ref_id=secrets.token_hex(4),
            referred_by=referred_by,
        )
        s.add(user)
        await s.commit()
        await s.refresh(user)
        return user


async def user_jobs(tg_id: int, limit: int = 20) -> list[Job]:
    async with SessionLocal() as s:
        rows = await s.scalars(select(Job).where(Job.tg_id == tg_id).order_by(desc(Job.created_at)).limit(limit))
        return list(rows)


async def create_job(tg_id: int, kind: str, tier: str, prompt: str, params: dict, inputs: list[str]) -> Job:
    async with SessionLocal() as s:
        job = Job(tg_id=tg_id, kind=kind, tier=tier, prompt=prompt, params=params, input_files=inputs)
        s.add(job)
        await s.commit()
        await s.refresh(job)
        return job


async def set_job(job_id: str, status: str, result_files: list[str] | None = None, error: str | None = None) -> None:
    async with SessionLocal() as s:
        job = await s.get(Job, job_id)
        if not job:
            return
        job.status = status
        if result_files is not None:
            job.result_files = result_files
        if error:
            job.error = error
        await s.commit()


async def charge_credits(tg_id: int, amount: int) -> bool:
    async with SessionLocal() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))
        if not user or user.credits < amount:
            return False
        user.credits -= amount
        await s.commit()
        return True


async def refund_credits(tg_id: int, amount: int) -> None:
    async with SessionLocal() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.credits += amount
            await s.commit()


async def create_payment(payload: str, tg_id: int, pack_id: str, stars: int, credits: int) -> None:
    async with SessionLocal() as s:
        s.add(Payment(payload=payload, tg_id=tg_id, pack_id=pack_id, stars=stars, credits_added=credits))
        await s.commit()


async def complete_payment(payload: str, charge_id: str) -> bool:
    async with SessionLocal() as s:
        payment = await s.scalar(select(Payment).where(Payment.payload == payload))
        if not payment:
            return False
        if payment.status == "paid":
            return False
        payment.status = "paid"
        payment.telegram_payment_charge_id = charge_id
        user = await s.scalar(select(User).where(User.tg_id == payment.tg_id))
        if user:
            user.credits += payment.credits_added
        await s.commit()
        return True


async def set_subscription(tg_id: int, days: int) -> None:
    async with SessionLocal() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return
        now = datetime.now(timezone.utc)
        base = user.subscription_end if user.subscription_end and user.subscription_end > now else now
        user.subscription_end = base + timedelta(days=days)
        await s.commit()


async def audit(actor_tg_id: int, action: str, meta: dict) -> None:
    async with SessionLocal() as s:
        s.add(AuditLog(actor_tg_id=actor_tg_id, action=action, meta=meta))
        await s.commit()
