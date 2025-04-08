from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states.registration import RegistrationStates

router = Router()

# TODO: Добавьте обработчики для регистрации работодателя (запрос ИНН, названия ООО/ИП)

@router.message(Command("employer_register"))
async def employer_register(message: types.Message, state: FSMContext):
    await message.answer("Начинаем регистрацию работодателя. Пожалуйста, введите ваш ИНН.")
    await state.set_state(RegistrationStates.employer_inn)

@router.message(RegistrationStates.employer_inn)
async def process_employer_inn(message: types.Message, state: FSMContext):
    await state.update_data(inn=message.text)
    await message.answer("Теперь введите название вашей организации (ООО/ИП).")
    await state.set_state(RegistrationStates.employer_name)

@router.message(RegistrationStates.employer_name)
async def process_employer_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(f"Вы указали ИНН: {user_data['inn']} и название: {message.text}. Регистрация завершена.")
    await state.clear()

# Другие обработчики