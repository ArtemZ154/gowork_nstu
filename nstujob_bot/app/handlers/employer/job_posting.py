# app/handlers/employer/add_job.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from ...states.employer_job_posting import AddPodrabotkaStates
import json
import os
import re

router = Router()
DATA_PATH_PODRABOTKI = "nstujob_bot/app/data/podrabotki.json"
DATA_PATH_USERS = "nstujob_bot/app/data/users.json"

def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} if path == DATA_PATH_USERS else []

def save_data(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

load_podrabotki = lambda: load_data(DATA_PATH_PODRABOTKI)
save_podrabotki = lambda data: save_data(data, DATA_PATH_PODRABOTKI)
load_users = lambda: load_data(DATA_PATH_USERS)
save_users = lambda data: save_data(data, DATA_PATH_USERS)

@router.message(lambda message: message.text and message.text.lower() == "добавить подработку")
async def employer_add_job_command(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users = load_users()
    employer_info = users.get(user_id)
    if employer_info and employer_info.get("role") == "employer" and employer_info.get("contacts"):
        stored_contacts = employer_info.get("contacts")
        await state.update_data(contact_info=stored_contacts)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Использовать эти контакты", callback_data="use_stored_contacts"),
                types.InlineKeyboardButton(text="Ввести новые", callback_data="enter_new_contacts")
            ]
        ])
        await state.set_state(AddPodrabotkaStates.contact_info)
        await message.answer(f"Использовать ваши сохраненные контакты: {stored_contacts}?", reply_markup=keyboard)
    else:
        await state.set_state(AddPodrabotkaStates.title)
        await message.answer("Введите название подработки:")

@router.callback_query(lambda c: c.data == "use_stored_contacts")
async def use_stored_contacts(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Контакты будут использованы.")
    await state.set_state(AddPodrabotkaStates.title)
    await callback.message.answer("Введите название подработки:")

@router.callback_query(lambda c: c.data == "enter_new_contacts")
async def enter_new_contacts(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Пожалуйста, введите ваши контактные данные.")
    await callback.message.answer("Введите вашу контактную информацию (например, номер телефона или Telegram):")
    await state.set_state(AddPodrabotkaStates.contact_info) # Переходим обратно к запросу контактов

@router.message(AddPodrabotkaStates.title)
async def process_podrabotka_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPodrabotkaStates.description)
    await message.answer("Теперь введите описание подработки (минимум 60 символов):")

@router.message(AddPodrabotkaStates.description)
async def process_podrabotka_description(message: types.Message, state: FSMContext):
    description = message.text
    if len(description) >= 60:
        await state.update_data(description=description)
        await state.set_state(AddPodrabotkaStates.payment)
        await message.answer("Укажите размер оплаты (только сумма):")
    else:
        await message.answer(f"Описание должно содержать не менее 60 символов. Сейчас {len(description)}.")

@router.message(AddPodrabotkaStates.payment)
async def process_podrabotka_payment(message: types.Message, state: FSMContext):
    payment = message.text
    payment_pattern = r"^\d+$"
    if re.match(payment_pattern, payment):
        await state.update_data(payment=payment)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Да", callback_data="mobility_friendly_yes"),
                types.InlineKeyboardButton(text="Нет", callback_data="mobility_friendly_no"),
            ],
        ])
        await state.set_state(AddPodrabotkaStates.mobility_friendly)
        await message.answer("Может ли маломобильный гражданин выполнять эту работу?", reply_markup=keyboard)
    else:
        await message.answer("Пожалуйста, введите только сумму оплаты (цифрами).")

@router.callback_query(AddPodrabotkaStates.mobility_friendly, lambda c: c.data in ["mobility_friendly_yes", "mobility_friendly_no"])
async def process_podrabotka_mobility_friendly(callback: types.CallbackQuery, state: FSMContext):
    mobility_friendly = callback.data == "mobility_friendly_yes"
    await state.update_data(mobility_friendly=mobility_friendly)
    await state.set_state(AddPodrabotkaStates.work_date)
    await callback.message.answer("Укажите дату выполнения работы в формате ГГГГ-ММ-ДД:")
    await callback.answer()

@router.message(AddPodrabotkaStates.work_date)
async def process_podrabotka_work_date(message: types.Message, state: FSMContext):
    work_date = message.text
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(date_pattern, work_date):
        await state.update_data(work_date=work_date)
        await state.set_state(AddPodrabotkaStates.work_time)
        await message.answer("Укажите время выполнения работы в формате ЧЧ:ММ (24-часовой формат):")
    else:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

@router.message(AddPodrabotkaStates.work_time)
async def process_podrabotka_work_time(message: types.Message, state: FSMContext):
    work_time = message.text
    time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if re.match(time_pattern, work_time):
        await state.update_data(work_time=work_time)
        await state.set_state(AddPodrabotkaStates.work_duration)
        await message.answer("Укажите приблизительную продолжительность работы в часах (целое число):")
    else:
        await message.answer("Некорректный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (24-часовой формат).")

@router.message(AddPodrabotkaStates.work_duration)
async def process_podrabotka_work_duration(message: types.Message, state: FSMContext):
    work_duration = message.text
    duration_pattern = r"^\d+$"
    if re.match(duration_pattern, work_duration):
        await state.update_data(work_duration=work_duration)
        # Если контакты уже были предзаполнены, пропускаем этот шаг
        data = await state.get_data()
        if not data.get("contact_info"):
            await state.set_state(AddPodrabotkaStates.contact_info)
            await message.answer("Введите вашу контактную информацию (например, номер телефона или Telegram):")
        else:
            await state.set_state(AddPodrabotkaStates.confirm)
            await show_confirmation(message, state)
    else:
        await message.answer("Некорректный формат продолжительности. Пожалуйста, введите продолжительность работы в часах (целое число).")

@router.message(AddPodrabotkaStates.contact_info)
async def process_podrabotka_contact_info(message: types.Message, state: FSMContext):
    await state.update_data(contact_info=message.text)
    await state.set_state(AddPodrabotkaStates.confirm)
    await show_confirmation(message, state)

async def show_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title", "Не указано")
    description = data.get("description", "Не указано")
    payment = data.get("payment", "Не указано")
    contact_info = data.get("contact_info", "Не указано")
    mobility_friendly = data.get("mobility_friendly", False)
    mobility_text = "Да" if mobility_friendly else "Нет"
    work_date = data.get("work_date", "Не указано")
    work_time = data.get("work_time", "Не указано")
    work_duration = data.get("work_duration", "Не указано")

    confirm_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm_podrabotka")],
        [types.InlineKeyboardButton(text="Отменить", callback_data="cancel_podrabotka")],
    ])

    await message.answer(
        f"Пожалуйста, проверьте введенные данные:\n\n"
        f"<b>Название:</b> {title}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Оплата:</b> {payment}\n"
        f"<b>Доступно для маломобильных:</b> {mobility_text}\n"
        f"<b>Дата работы:</b> {work_date}\n"
        f"<b>Время работы:</b> {work_time}\n"
        f"<b>Продолжительность:</b> {work_duration} часов\n"
        f"<b>Контакты:</b> {contact_info}\n\n"
        f"Подтвердить публикацию?",
        reply_markup=confirm_keyboard,
        parse_mode="HTML"
    )

@router.callback_query(AddPodrabotkaStates.confirm, lambda c: c.data == "confirm_podrabotka")
async def process_podrabotka_confirmation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    podrabotki = load_podrabotki()
    new_podrabotka = {
        "id": len(podrabotki) + 1,  # Простой способ генерации ID
        "title": data.get("title", "Не указано"),
        "description": data.get("description", "Не указано"),
        "payment": data.get("payment", "Не указано"),
        "contact_info": data.get("contact_info", "Не указано"),
        "employer_id": callback.from_user.id, # Сохраняем ID работодателя
        "mobility_friendly": data.get("mobility_friendly", False), # Сохраняем информацию о доступности
        "work_date": data.get("work_date", "Не указано"), # Сохраняем дату работы
        "work_time": data.get("work_time", "Не указано"), # Сохраняем время работы
        "work_duration": data.get("work_duration", "Не указано") # Сохраняем продолжительность работы
    }
    podrabotki.append(new_podrabotka)
    save_podrabotki(podrabotki)
    await callback.message.answer("Предложение подработки успешно опубликовано!")
    await state.clear()
    await callback.answer()

@router.callback_query(AddPodrabotkaStates.confirm, lambda c: c.data == "cancel_podrabotka")
async def process_podrabotka_cancellation(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Добавление подработки отменено.")
    await state.clear()
    await callback.answer()
