# app/handlers/common.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command

# Можно импортировать тексты из lexicon
# from app.lexicon.lexicon_ru import LEXICON_RU

# Создаем роутер для общих команд
common_router = Router(name="common_commands")

@common_router.message(CommandStart())
async def handle_start(message: types.Message):
    # Здесь будет логика для команды /start
    # Например, приветствие и показ главного меню в зависимости от статуса пользователя
    user_id = message.from_user.id
    # TODO: Проверить, зарегистрирован ли user_id и какая у него роль
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот для поиска подработки в НГТУ.")
    # await message.answer(LEXICON_RU['start']) # Пример с лексиконом

@common_router.message(Command("help"))
async def handle_help(message: types.Message):
    # Логика для команды /help
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        # TODO: Добавить другие общие команды или описание функционала
    )
    await message.answer(help_text)

# Другие общие хэндлеры (например, обработка неизвестных команд/сообщений)
# @common_router.message()
# async def handle_unknown(message: types.Message):
#     await message.answer("Извините, я не понимаю эту команду. Используйте /help для списка команд.")
# app/handlers/common.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command

# Можно импортировать тексты из lexicon
# from app.lexicon.lexicon_ru import LEXICON_RU

# Создаем роутер для общих команд
common_router = Router(name="common_commands")

@common_router.message(CommandStart())
async def handle_start(message: types.Message):
    # Здесь будет логика для команды /start
    # Например, приветствие и показ главного меню в зависимости от статуса пользователя
    user_id = message.from_user.id
    # TODO: Проверить, зарегистрирован ли user_id и какая у него роль
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот для поиска подработки в НГТУ.")
    # await message.answer(LEXICON_RU['start']) # Пример с лексиконом

@common_router.message(Command("help"))
async def handle_help(message: types.Message):
    # Логика для команды /help
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        # TODO: Добавить другие общие команды или описание функционала
    )
    await message.answer(help_text)

# Другие общие хэндлеры (например, обработка неизвестных команд/сообщений)
# @common_router.message()
# async def handle_unknown(message: types.Message):
#     await message.answer("Извините, я не понимаю эту команду. Используйте /help для списка команд.")