import secrets

from aiogram import F, Router
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from bot.app.services.repository import complete_payment, create_payment
from common.config import get_settings

cfg = get_settings()
router = Router()


@router.message(F.text == "💳 Пополнить")
async def buy(message: Message) -> None:
    payload = f"starter:{secrets.token_hex(6)}"
    await create_payment(payload, message.from_user.id, "starter", cfg.pack_starter_stars, cfg.pack_starter_credits)
    await message.answer_invoice(
        title="Starter pack",
        description="60 credits",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label="Starter", amount=cfg.pack_starter_stars)],
        provider_token="",
    )


@router.callback_query(F.data == "buy_starter")
async def buy_cb(cb):
    await buy(cb.message)
    await cb.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def success(message: Message) -> None:
    pay = message.successful_payment
    changed = await complete_payment(pay.invoice_payload, pay.telegram_payment_charge_id)
    text = "Оплата принята, кредиты начислены." if changed else "Оплата уже была обработана ранее."
    await message.answer(text)
