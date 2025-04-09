# app/handlers/registration.py
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from ..states.registration import RegistrationStates
from ..keyboards.role import role_keyboard
from ..keyboards.main_menu import get_main_keyboard
import json
import os
import re

router = Router()
DATA_PATH = "nstujob_bot/app/data/users.json"
GROUP_DATA_PATH = 'nstujob_bot/app/data/group_id.json'

def load_users():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_PATH, 'w') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def load_group_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return []  # Возвращаем пустой список
    except json.JSONDecodeError:
        print(f"Ошибка: Некорректный формат JSON в файле '{file_path}'.")
        return []  # Возвращаем пустой список

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id in users:
        user_role = users[user_id]['role']
        keyboard = get_main_keyboard(user_role)
        await message.answer(f"Добро пожаловать, {user_role}!", reply_markup=keyboard)
    else:
        await state.set_state(RegistrationStates.role)
        await message.answer("Выберите свою роль:", reply_markup=role_keyboard)

@router.message(RegistrationStates.role)
async def process_role(message: types.Message, state: FSMContext):
    if message.text == "Студент":
        await state.update_data(role="student")
        await state.set_state(RegistrationStates.student_group)
        await message.answer("Введите номер вашей группы:")
    elif message.text == "Работодатель":
        await state.update_data(role="employer")
        await state.set_state(RegistrationStates.employer_name)
        await message.answer("Введите название вашей организации:")
    else:
        await message.answer("Пожалуйста, выберите одну из предложенных ролей.")

# Регистрация студента
@router.message(RegistrationStates.student_group)
async def process_student_group(message: types.Message, state: FSMContext):
    group_name = message.text.strip()
    group_data = load_group_data(GROUP_DATA_PATH)
    found_group_id = None

    for group_info in group_data:
        if group_info.get("NAME") == group_name:
            found_group_id = group_info.get("ID")
            break  # Нашли совпадение, можно выйти из цикла

    if found_group_id:
        await state.update_data(group=found_group_id)  # Сохраняем ID группы
        await state.set_state(RegistrationStates.student_contacts)
        await message.answer(f"Название группы '{group_name}' найдено. ID группы: {found_group_id}")
        await message.answer("Введите ваш Telegram (@username) или номер телефона (+7XXXXXXXXXX):")
    else:
        await message.answer(
            f"Название группы '{group_name}' не найдено в списке. Пожалуйста, введите точное название группы.")
        # Не переходим к следующему состоянию, остаемся в текущем, чтобы пользователь

@router.message(RegistrationStates.student_contacts)
async def process_student_contacts(message: types.Message, state: FSMContext):
    contacts = message.text
    telegram_pattern = r"^@[\w_]+$"
    phone_pattern = r"^\+7\d{10}$"
    if re.match(telegram_pattern, contacts) or re.match(phone_pattern, contacts):
        await state.update_data(contacts=contacts)
        await state.set_state(RegistrationStates.student_full_name)
        await message.answer("Введите ваше ФИО (только на русском языке):")
    else:
        await message.answer("Некорректный формат контактов. Пожалуйста, введите Telegram (@username) или номер телефона (+7XXXXXXXXXX).")

@router.message(RegistrationStates.student_full_name)
async def process_student_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    russian_pattern = r"^[а-яА-ЯёЁ\s]+$"
    if re.match(russian_pattern, full_name):
        await state.update_data(full_name=full_name)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Да", callback_data="mobility_yes"),
                types.InlineKeyboardButton(text="Нет", callback_data="mobility_no"),
            ],
        ])
        await state.set_state(RegistrationStates.student_mobility)
        await message.answer("Являетесь ли вы маломобильным гражданином?", reply_markup=keyboard)
    else:
        await message.answer("ФИО должно быть написано только на русском языке.")

@router.callback_query(RegistrationStates.student_mobility, lambda c: c.data in ["mobility_yes", "mobility_no"])
async def process_student_mobility(callback: types.CallbackQuery, state: FSMContext):
    mobility = callback.data == "mobility_yes"
    await state.update_data(mobility=mobility)
    user_data = await state.get_data()
    users = load_users()
    user_id = str(callback.from_user.id)
    users[user_id] = {
        "role": user_data.get("role"),
        "group": user_data.get("group"),
        "contacts": user_data.get("contacts"),
        "full_name": user_data.get("full_name"),
        "mobility": user_data.get("mobility")
    }
    save_users(users)
    keyboard = get_main_keyboard("student")
    mobility_status = "являетесь" if mobility else "не являетесь"
    await callback.message.answer(f"Регистрация студента {user_data.get('full_name')} завершена! Ваша группа: {user_data.get('group')}, контакты: {user_data.get('contacts')}. Вы {mobility_status} маломобильным гражданином.", reply_markup=keyboard)
    await state.clear()
    await callback.answer()

# Регистрация работодателя (без изменений для этого шага)
@router.message(RegistrationStates.employer_name)
async def process_employer_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.employer_contacts)
    await message.answer("Введите контактный номер телефона (+7XXXXXXXXXX):")

@router.message(RegistrationStates.employer_contacts)
async def process_employer_contacts(message: types.Message, state: FSMContext):
    contacts = message.text
    phone_pattern = r"^\+7\d{10}$"
    if re.match(phone_pattern, contacts):
        await state.update_data(contacts=contacts)
        await state.set_state(RegistrationStates.employer_full_name)
        await message.answer("Введите ФИО ответственного лица (только на русском языке):")
    else:
        await message.answer("Некорректный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX.")

@router.message(RegistrationStates.employer_full_name)
async def process_employer_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    russian_pattern = r"^[а-яА-ЯёЁ\s]+$"
    if re.match(russian_pattern, full_name):
        await state.update_data(full_name=full_name)
        user_data = await state.get_data()
        users = load_users()
        user_id = str(message.from_user.id)
        users[user_id] = {
            "role": user_data.get("role"),
            "name": user_data.get("name"),
            "contacts": user_data.get("contacts"),
            "full_name": user_data.get("full_name")
        }
        save_users(users)
        keyboard = get_main_keyboard("employer")
        await message.answer(f"Регистрация работодателя {user_data.get('name')} (ответственное лицо: {user_data.get('full_name')}, контакты: {user_data.get('contacts')}) завершена!", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("ФИО должно быть написано только на русском языке.")