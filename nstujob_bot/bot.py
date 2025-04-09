# bot.py
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

# --- Импорт конфигурации ---
try:
    from app.config.settings import settings
except ImportError:
    logging.critical("Не удалось импортировать настройки. Убедитесь, что app/config/settings.py существует и настроен.")
    sys.exit(1)

# --- Импорт основных компонентов приложения ---
from app.handlers import main_router # Главный роутер (общие команды)
from app.handlers import registration # Роутер для регистрации
from app.middlewares.auth import AuthMiddleware # Middleware для аутентификации

# --- Настройка логирования ---
log_level = logging.INFO
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout)
logger = logging.getLogger(__name__)

async def main() -> None:
    logger.info("Запуск бота...")
    storage = MemoryStorage()
    try:
        bot_token = settings.bot_token.get_secret_value()
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except AttributeError:
         logger.critical("Не найден BOT_TOKEN в настройках!")
         sys.exit(1)
    except Exception as e:
        logger.critical(f"Ошибка инициализации Bot API: {e}")
        sys.exit(1)

    dp = Dispatcher(storage=storage)
    logger.info("Bot и Dispatcher инициализированы.")

    # --- Регистрация Middleware ---
    dp.update.middleware.register(AuthMiddleware()) # Регистрируем AuthMiddleware

    # --- Регистрация Роутеров ---
    dp.include_router(registration.router) # Подключаем роутер регистрации
    dp.include_router(main_router) # Подключаем основной роутер
    logger.info("Роутеры подключены.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        if hasattr(storage, 'close'):
           await storage.close()
        logger.info("Сессия бота и хранилище закрыты.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"Неперехваченное исключение: {e}", exc_info=True)
        sys.exit(1)