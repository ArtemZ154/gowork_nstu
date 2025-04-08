from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# TODO: Добавьте обработчики для создания/удаления работы (админом)

@router.message(Command("admin_create_job"))
async def admin_create_job(message: types.Message):
    await message.answer("Обработка создания вакансии (админ)")

@router.message(Command("admin_delete_job"))
async def admin_delete_job(message: types.Message):
    await message.answer("Обработка удаления вакансии (админ)")

# Другие обработчики