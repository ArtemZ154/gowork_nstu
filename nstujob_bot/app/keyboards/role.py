from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Студент"),
            KeyboardButton(text="Работодатель"),
        ],
    ],
    resize_keyboard=True
)