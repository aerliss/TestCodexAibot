from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credits: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[str] = mapped_column(String(16), default="standard")
    free_granted: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(8), default="ru")
    subscription_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ref_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    kind: Mapped[str] = mapped_column(String(16))
    tier: Mapped[str] = mapped_column(String(16))
    prompt: Mapped[str] = mapped_column(Text)
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    input_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="queued")
    result_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    moderated: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    payload: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    pack_id: Mapped[str] = mapped_column(String(32))
    stars: Mapped[int] = mapped_column(Integer)
    credits_added: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    telegram_payment_charge_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    referred_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    reward_credits: Mapped[int] = mapped_column(Integer, default=10)


class SubscriptionLog(Base):
    __tablename__ = "subscription_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(32))
    stars: Mapped[int] = mapped_column(Integer)
    period_days: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(64))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
