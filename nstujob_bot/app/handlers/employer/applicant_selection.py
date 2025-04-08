from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# TODO: Добавьте обработчики для просмотра откликов и выбора кандидата

@router.message(Command("employer_view_applicants"))
async def employer_view_applicants(message: types.Message):
    await message.answer("Список откликнувшихся на ваши вакансии:")
    # TODO: Реализуйте логику получения и отображения откликов
    pass

@router.message(Command("employer_select_applicant"))
async def employer_select_applicant(message: types.Message):
    await message.answer("Введите ID пользователя, которого вы хотите подтвердить:")
    # TODO: Реализуйте логику выбора кандидата и отправки уведомления
    pass

# Другие обработчики