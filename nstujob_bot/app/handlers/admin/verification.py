from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# TODO: Добавьте обработчики для верификации пользователей (студентов/работодателей)

@router.message(Command("admin_verify_student"))
async def admin_verify_student(message: types.Message):
    await message.answer("Обработка верификации студента (админ)")

@router.message(Command("admin_verify_employer"))
async def admin_verify_employer(message: types.Message):
    await message.answer("Обработка верификации работодателя (админ)")

# Другие обработчики