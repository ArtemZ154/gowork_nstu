# app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import Optional
from dotenv import load_dotenv
import os
import logging

# Загружаем переменные окружения из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
print("Значение BOT_TOKEN:", os.environ.get("BOT_TOKEN"))

class Settings(BaseSettings):
    """Настройки приложения."""
    bot_token: SecretStr  # Для хранения токена бота (защищенный тип)
    database_url: Optional[str] = None  # URL для подключения к базе данных (опционально)
    redis_dsn: Optional[str] = None  # URL для подключения к Redis (опционально)
    log_level: str = "INFO"  # Уровень логирования по умолчанию

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

# Создаем экземпляр настроек
settings = Settings()

# Настраиваем базовое логирование (можно настроить более детально в bot.py)
logging.basicConfig(level=settings.log_level.upper(), format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Настройки приложения загружены.")
logger.debug(f"Текущие настройки: {settings.dict()}")

if __name__ == "__main__":
    print("Проверка настроек:")
    print(f"Токен бота: {settings.bot_token.get_secret_value()[:10]}...") # Показываем только первые 10 символов
    print(f"URL базы данных: {settings.database_url}")
    print(f"URL Redis: {settings.redis_dsn}")
    print(f"Уровень логирования: {settings.log_level}")