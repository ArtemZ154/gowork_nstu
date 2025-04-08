from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states.job_posting import JobPostingStates

router = Router()

# TODO: Добавьте обработчики для создания и публикации вакансий

@router.message(Command("employer_post_job"))
async def employer_post_job(message: types.Message, state: FSMContext):
    await message.answer("Начинаем создание вакансии. Введите тип работы.")
    await state.set_state(JobPostingStates.job_type)

# Добавьте другие обработчики для заполнения полей вакансии (описание, зарплата, время поиска и т.д.)