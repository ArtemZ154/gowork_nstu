from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# TODO: Добавьте обработчики для блокировки/разблокировки пользователей

@router.message(Command("admin_block_user"))
async def admin_block_user(message: types.Message):
    await message.answer("Обработка блокировки пользователя (админ)")

@router.message(Command("admin_unblock_user"))
async def admin_unblock_user(message: types.Message):
    await message.answer("Обработка разблокировки пользователя (админ)")

# Другие обработчики