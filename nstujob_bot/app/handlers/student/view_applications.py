from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# TODO: Добавьте обработчики для просмотра и удаления своих откликов

@router.message(Command("student_view_applications"))
async def student_view_applications(message: types.Message):
    await message.answer("Список ваших откликов:")
    # TODO: Реализуйте логику получения и отображения откликов студента
    pass

@router.message(Command("student_delete_application"))
async def student_delete_application(message: types.Message):
    await message.answer("Введите ID отклика, который вы хотите удалить:")
    # TODO: Реализуйте логику удаления отклика студентом
    pass

# Другие обработчики