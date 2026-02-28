from __future__ import annotations

import secrets

from aiogram import F, Router
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from bot.app.services.repository import add_payment, complete_payment
from common.config import get_settings

router = Router()
cfg = get_settings()


@router.message(F.text == "💳 Пополнить")
async def topup_menu(message: Message) -> None:
    payload = f"starter:{secrets.token_hex(6)}"
    await add_payment(payload, message.from_user.id, "starter", cfg.pack_starter_stars, cfg.pack_starter_credits)
    await message.answer_invoice(
        title="Starter pack",
        description="60 credits for AI image/video generation",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label="Starter", amount=cfg.pack_starter_stars)],
        provider_token="",
    )


@router.callback_query(F.data == "buy_starter")
async def auto_buy(callback):
    await topup_menu(callback.message)
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    pay = message.successful_payment
    await complete_payment(pay.invoice_payload, pay.telegram_payment_charge_id)
    await message.answer("Оплата прошла успешно, кредиты зачислены.")
