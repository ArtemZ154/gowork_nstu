# app/middlewares/auth.py
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import json
import os

DATA_PATH = "nstujob_bot/app/data/users.json"
print(os.path.exists(DATA_PATH))
def load_users():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    return {}

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user and user.id:
            users = load_users()
            user_id = str(user.id)
            if user_id in users:
                data["user_role"] = users[user_id]["role"]
                return await handler(event, data)
            else:
                if isinstance(event, Message):
                    await event.answer("Вы не зарегистрированы. Используйте команду /start для регистрации.")
                elif isinstance(event, CallbackQuery):
                    await event.message.answer("Вы не зарегистрированы. Используйте команду /start для регистрации.")
                return
        else:
            # Обработка событий без информации о пользователе (например, служебные обновления)
            return await handler(event, data)

    # def __init__(self, db_pool: ConnectionPool): # Пример принятия зависимостей
    #     self.db_pool = db_pool