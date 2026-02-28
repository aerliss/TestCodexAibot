from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from common.config import get_settings


def main_menu() -> ReplyKeyboardMarkup:
    cfg = get_settings()
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖼 Генерация"), KeyboardButton(text="🎬 Видео")],
            [KeyboardButton(text="🛠 Редактирование"), KeyboardButton(text="💳 Пополнить")],
            [KeyboardButton(text="⚙️ Tier"), KeyboardButton(text="🌐 Язык")],
            [KeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{cfg.webapp_base_url}/cabinet"))],
        ],
        resize_keyboard=True,
    )
