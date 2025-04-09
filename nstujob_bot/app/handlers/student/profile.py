from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from ...states.profile import ProfileStates
import json
import os

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
        json.dump(users, f, indent=4)

def load_group_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка: Некорректный формат JSON в файле '{file_path}'.")
        return []


@router.message(lambda message: message.text and message.text.lower() == "профиль")
async def show_profile_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Изменить группу", callback_data="change_group")],
        [types.InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_account")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "change_group")
async def start_change_group(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.change_group)
    await callback.message.answer("Введите новый номер группы:")
    await callback.answer()

@router.message(ProfileStates.change_group)
async def process_new_group(message: types.Message, state: FSMContext):
    """Обработчик для ввода нового названия группы и его перевода в ID."""
    new_group_name = message.text.strip()
    group_data = load_group_data(GROUP_DATA_PATH)
    found_group_id = None

    for group_info in group_data:
        if group_info.get("NAME") == new_group_name:
            found_group_id = group_info.get("ID")
            break

    if found_group_id:
        # Здесь должна быть логика обновления группы пользователя в вашей базе данных
        user_id = message.from_user.id  # Получаем ID пользователя
        # Пример: await update_user_group(user_id, found_group_id)
        await message.answer(f"Название группы '{new_group_name}' найдено. ID группы: {found_group_id}")
        await message.answer(f"Ваша группа успешно обновлена на ID: {found_group_id}")
        await state.clear()  # Завершаем состояние изменения группы
    else:
        await message.answer(f"Название группы '{new_group_name}' не найдено в списке. Пожалуйста, введите точное название группы.")
        # Не переходим в следующее состояние, остаемся в ProfileStates.change_group
        # чтобы пользователь мог ввести название снова

@router.callback_query(lambda c: c.data == "delete_account")
async def confirm_delete_account(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Да, удалить", callback_data="confirm_delete")],
        [types.InlineKeyboardButton(text="Нет, отмена", callback_data="cancel_delete")]
    ])
    await callback.message.answer("Вы уверены, что хотите удалить свой аккаунт?", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "confirm_delete")
async def delete_account(callback: types.CallbackQuery):
    users = load_users()
    user_id = str(callback.from_user.id)
    print(f"User ID при попытке удалить аккаунт: {user_id}")
    print(f"Содержимое users.json: {users}")
    if user_id in users:
        del users[user_id]
        save_users(users)
        await callback.message.answer("Ваш аккаунт успешно удален.")
    else:
        await callback.message.answer("Произошла ошибка при удалении аккаунта.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel_delete")
async def cancel_delete_account(callback: types.CallbackQuery):
    await callback.message.answer("Удаление аккаунта отменено.")
    await callback.answer()