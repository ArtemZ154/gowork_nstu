from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
import logging


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех входящих сообщений"""

    async def on_pre_process_message(self, message: types.Message, data: dict):
        # Вызывается ПЕРЕД обработкой сообщения
        logging.info(f"User {message.from_user.id} sent: {message.text}")

    async def on_process_message(self, message: types.Message, data: dict):
        # Вызывается ВО ВРЕМЯ обработки
        pass  # Можно добавить дополнительную логику

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        # Вызывается ПОСЛЕ обработки
        logging.info(f"Message processing completed for {message.from_user.id}")


class AccessMiddleware(BaseMiddleware):
    """Middleware для проверки прав доступа"""

    def __init__(self, allowed_roles: list):
        super().__init__()
        self.allowed_roles = allowed_roles

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_role = data.get('role', 'guest')

        if user_role not in self.allowed_roles:
            await message.answer("🚫 У вас нет доступа к этой команде!")
            raise CancelHandler()


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для защиты от спама"""

    def __init__(self, limit: int = 3):
        self.limit = limit
        self.user_requests = {}  # {user_id: count}

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        current = self.user_requests.get(user_id, 0)

        if current >= self.limit:
            await message.answer("⏳ Слишком много запросов! Подождите...")
            raise CancelHandler()

        self.user_requests[user_id] = current + 1
