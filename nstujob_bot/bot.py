# bot.py
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage # Для начала используем хранилище в памяти
# Для продакшена рассмотрите Redis:
# from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
# from redis.asyncio.client import Redis

# --- Импорт конфигурации ---
# Предполагается, что settings загружает конфигурацию из .env
# Убедитесь, что app.config.settings существует и работает
try:
    from app.config.settings import settings
except ImportError:
    logging.critical("Не удалось импортировать настройки. Убедитесь, что app/config/settings.py существует и настроен.")
    sys.exit(1)

# --- Импорт основных компонентов приложения ---
from app.handlers import main_router # Главный роутер, собранный в app/handlers/__init__.py
# from app.middlewares.access import AccessMiddleware # Если есть middleware для проверки доступа
# from app.database.connection import setup_db, shutdown_db # Опционально: функции для управления подключением к БД

# --- Настройка логирования ---
log_level = logging.INFO # Или settings.LOG_LEVEL, если он есть в конфиге
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout)
logger = logging.getLogger(__name__)

async def main() -> None:
    """Главная функция для инициализации и запуска бота."""
    logger.info("Запуск бота...")

    # --- Инициализация хранилища FSM ---
    # Для продакшена замените на RedisStorage или другое персистентное хранилище
    storage = MemoryStorage()
    # Пример для Redis:
    # redis_client = Redis.from_url(settings.REDIS_DSN)
    # storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_destiny=True))
    # logger.info(f"Используется Redis FSM Storage: {settings.REDIS_DSN}")

    # --- Инициализация бота и диспетчера ---
    try:
        # Используем get_secret_value() для безопасного получения токена из Pydantic SecretStr
        bot_token = settings.bot_token.get_secret_value()
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))# или MARKDOWN_V2
    except AttributeError:
         logger.critical("Не найден BOT_TOKEN в настройках!")
         sys.exit(1)
    except Exception as e:
        logger.critical(f"Ошибка инициализации Bot API: {e}")
        sys.exit(1)


    dp = Dispatcher(storage=storage)
    logger.info("Bot и Dispatcher инициализированы.")

    # --- Регистрация Middleware ---
    # Порядок важен! AuthMiddleware должен идти раньше AccessMiddleware, если второй зависит от данных первого.
    # Передавайте необходимые зависимости (например, пул соединений с БД) в middleware при инициализации, если нужно.
    # db_pool = await setup_db(...) # Пример получения пула соединений
    # dp.update.outer_middleware.register(AccessMiddleware()) # Раскомментируйте, если используете
    logger.info("Middlewares зарегистрированы.")

    # --- Регистрация Роутеров ---
    dp.include_router(main_router)
    logger.info("Роутеры подключены.")

    # --- Настройка и отключение зависимостей (например, БД) ---
    # Если у вас есть асинхронные функции для установки и закрытия соединения с БД:
    # dp.startup.register(setup_db) # Можно передать аргументы: setup_db(arg1=...)
    # dp.shutdown.register(shutdown_db)
    # logger.info("Хуки для управления подключением к БД зарегистрированы.")

    # --- Запуск процесса polling ---
    try:
        # Удаляем вебхук перед запуском polling, если он был установлен
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален.")
        # Запускаем получение обновлений
        await dp.start_polling(bot) # Можно передать allowed_updates для фильтрации типов обновлений
    finally:
        # Корректное закрытие сессии бота при остановке
        await bot.session.close()
        # Корректное закрытие хранилища (если требуется, например, для Redis)
        if hasattr(storage, 'close'):
           await storage.close()
        logger.info("Сессия бота и хранилище закрыты.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        # Логируем критическую ошибку перед падением
        logger.critical(f"Неперехваченное исключение: {e}", exc_info=True)
        sys.exit(1) # Выход с кодом ошибки