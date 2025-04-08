from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states.registration import RegistrationStates

router = Router()

# TODO: Добавьте обработчики для регистрации студента (запрос группы)

@router.message(Command("student_register"))
async def student_register(message: types.Message, state: FSMContext):
    await message.answer("Начинаем регистрацию студента. Пожалуйста, введите номер вашей группы.")
    await state.set_state(RegistrationStates.student_group)

@router.message(RegistrationStates.student_group)
async def process_student_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(f"Вы указали группу: {message.text}. Регистрация завершена.")
    await state.clear()

# Другие обработчики