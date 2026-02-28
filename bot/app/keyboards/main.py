from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from common.config import get_settings
from common.security import WebAppSigner


def main_menu(tg_id: int) -> ReplyKeyboardMarkup:
    cfg = get_settings()
    signer = WebAppSigner()
    auth = signer.sign_tg_id(tg_id)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖼 Генерация"), KeyboardButton(text="🎬 Видео")],
            [KeyboardButton(text="🛠 Редактирование"), KeyboardButton(text="💳 Пополнить")],
            [KeyboardButton(text="⚙️ Tier"), KeyboardButton(text="🌐 Язык")],
            [KeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{cfg.webapp_base_url}/cabinet?auth={auth}"))],
        ],
        resize_keyboard=True,
    )
