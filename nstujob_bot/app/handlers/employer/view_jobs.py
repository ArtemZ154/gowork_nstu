# app/handlers/employer/view_jobs.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from ...states.employer_job_posting import AddPodrabotkaStates, EditPodrabotkaStates
import re
import json
import os

router = Router()
DATA_PATH = "nstujob_bot/app/data/podrabotki.json"

def load_podrabotki():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_podrabotki(podrabotki):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(podrabotki, f, indent=4, ensure_ascii=False)

@router.message(lambda message: message.text and message.text.lower() == "мои предложения")
async def view_employer_jobs(message: types.Message):
    employer_id = message.from_user.id
    podrabotki = load_podrabotki()
    employer_offers = [
        p for p in podrabotki if p.get("employer_id") == employer_id
    ]

    if not employer_offers:
        await message.answer("У вас пока нет опубликованных предложений подработки.")
        return

    for offer in employer_offers:
        title = offer.get("title", "Без названия")
        description = offer.get("description", "Описание отсутствует")
        payment = offer.get("payment", "Не указано")
        offer_id = offer.get("id", "Неизвестно")
        work_date = offer.get("work_date", "Неизвестно")
        work_time = offer.get("work_time", "Неизвестно")
        work_duration = offer.get("work_duration", "Неизвестно")

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit_podrabotka_{offer_id}"),
                types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_podrabotka_{offer_id}")
            ]
        ])

        text = f"<b>Название:</b> {title}\n"
        text += f"<b>Описание:</b> {description[:50]}...\n"
        text += f"<b>Оплата:</b> {payment}\n"
        text += f"<b>Дата:</b> {work_date}\n"
        text += f"<b>Время:</b> {work_time}\n"
        text += f"<b>Продолжительность:</b> {work_duration} часов\n"

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("delete_podrabotka_"))
async def confirm_delete_podrabotka(callback: types.CallbackQuery):
    offer_id = int(callback.data.split("_")[2])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Да, удалить", callback_data=f"confirm_delete_{offer_id}"),
            types.InlineKeyboardButton(text="Нет, отмена", callback_data="cancel_delete")
        ]
    ])
    await callback.message.answer(f"Вы уверены, что хотите удалить предложение подработки с ID: {offer_id}?", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def delete_podrabotka(callback: types.CallbackQuery):
    offer_id = int(callback.data.split("_")[2])
    employer_id = callback.from_user.id
    podrabotki = load_podrabotki()
    updated_podrabotki = [p for p in podrabotki if not (p.get("id") == offer_id and p.get("employer_id") == employer_id)]
    if len(updated_podrabotki) < len(podrabotki):
        save_podrabotki(updated_podrabotki)
        await callback.message.answer(f"Предложение подработки с ID: {offer_id} успешно удалено.")
    else:
        await callback.message.answer("Произошла ошибка при удалении предложения.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel_delete")
async def cancel_delete_podrabotka(callback: types.CallbackQuery):
    await callback.message.answer("Удаление отменено.")
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("edit_podrabotka_"))
async def edit_podrabotka_menu(callback: types.CallbackQuery, state: FSMContext):
    offer_id = int(callback.data.split("_")[2])
    await state.update_data(edit_offer_id=offer_id)
    await state.set_state(EditPodrabotkaStates.menu)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Название", callback_data="edit_title")],
        [types.InlineKeyboardButton(text="Описание", callback_data="edit_description")],
        [types.InlineKeyboardButton(text="Оплата", callback_data="edit_payment")],
        [types.InlineKeyboardButton(text="Контакты", callback_data="edit_contact_info")],
        [types.InlineKeyboardButton(text="Дата", callback_data="edit_date")],
        [types.InlineKeyboardButton(text="Время", callback_data="edit_time")],
        [types.InlineKeyboardButton(text="Продолжительность", callback_data="edit_duration")],
        [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_edit")]
    ])
    await callback.message.answer("Выберите поле для редактирования:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel_edit")
async def cancel_edit_podrabotka(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Редактирование отменено.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "edit_title")
async def edit_title(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.title)
    await callback.message.answer("Введите новое название предложения:")
    await callback.answer()

@router.message(EditPodrabotkaStates.title)
async def process_new_title(message: types.Message, state: FSMContext):
    new_title = message.text
    job_id_data = await state.get_data()
    job_id = job_id_data.get("edit_offer_id")
    if await update_job_data(job_id, "title", new_title, message):
        await state.set_state(EditPodrabotkaStates.menu)
        await message.answer(f"Название успешно обновлено на '{new_title}'.")
    else:
        await message.answer(f"Не удалось обновить название для подработки с ID {job_id}.")

@router.callback_query(lambda c: c.data == "edit_description")
async def edit_description(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.description)
    await callback.message.answer("Введите новое описание предложения:")
    await callback.answer()

@router.message(EditPodrabotkaStates.description)
async def process_new_description(message: types.Message, state: FSMContext):
    new_description = message.text
    job_id_data = await state.get_data()
    job_id = job_id_data.get("edit_offer_id")
    if await update_job_data(job_id, "description", new_description, message):
        await state.set_state(EditPodrabotkaStates.menu)
        await message.answer(f"Описание успешно обновлено на '{new_description}'.")
    else:
        await message.answer(f"Не удалось обновить описание для подработки с ID {job_id}.")

@router.callback_query(lambda c: c.data == "edit_payment")
async def edit_payment(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.payment)
    await callback.message.answer("Введите новую оплату:")
    await callback.answer()

@router.message(EditPodrabotkaStates.payment)
async def process_new_payment(message: types.Message, state: FSMContext):
    new_payment = message.text
    job_id_data = await state.get_data()
    job_id = job_id_data.get("edit_offer_id")
    if await update_job_data(job_id, "payment", new_payment, message):
        await state.set_state(EditPodrabotkaStates.menu)
        await message.answer(f"Оплата успешно обновлена на '{new_payment}'.")
    else:
        await message.answer(f"Не удалось обновить оплату для подработки с ID {job_id}.")

@router.callback_query(lambda c: c.data == "edit_contact_info")
async def edit_contact_info(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.contact_info)
    await callback.message.answer("Введите новую контактную информацию:")
    await callback.answer()

@router.message(EditPodrabotkaStates.contact_info)
async def process_new_contact_info(message: types.Message, state: FSMContext):
    new_contact_info = message.text
    job_id_data = await state.get_data()
    job_id = job_id_data.get("edit_offer_id")
    if await update_job_data(job_id, "contact_info", new_contact_info, message):
        await state.set_state(EditPodrabotkaStates.menu)
        await message.answer(f"Контактная информация успешно обновлена на '{new_contact_info}'.")
    else:
        await message.answer(f"Не удалось обновить контактную информацию для подработки с ID {job_id}.")

@router.callback_query(lambda c: c.data == "edit_date")
async def edit_date(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.work_date)
    await callback.message.answer("Введите новую дату выполнения работы в формате ГГГГ-ММ-ДД:")
    await callback.answer()

@router.message(EditPodrabotkaStates.work_date)
async def process_new_date(message: types.Message, state: FSMContext):
    work_date = message.text
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(date_pattern, work_date):
        job_id_data = await state.get_data()
        job_id = job_id_data.get("edit_offer_id")
        if await update_job_data(job_id, "work_date", work_date, message):
            await state.set_state(EditPodrabotkaStates.menu)
            await message.answer(f"Дата успешно обновлена на '{work_date}'.")
        else:
            await message.answer(f"Не удалось обновить дату для подработки с ID {job_id}.")
    else:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

@router.callback_query(lambda c: c.data == "edit_time")
async def edit_time(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.work_time)
    await callback.message.answer("Введите новое время выполнения работы в формате ЧЧ:ММ (24-часовой формат):")
    await callback.answer()

@router.message(EditPodrabotkaStates.work_time)
async def process_new_time(message: types.Message, state: FSMContext):
    work_time = message.text
    time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if re.match(time_pattern, work_time):
        job_id_data = await state.get_data()
        job_id = job_id_data.get("edit_offer_id")
        if await update_job_data(job_id, "work_time", work_time, message):
            await state.set_state(EditPodrabotkaStates.menu)
            await message.answer(f"Время успешно обновлено на '{work_time}'.")
        else:
            await message.answer(f"Не удалось обновить время для подработки с ID {job_id}.")
    else:
        await message.answer("Некорректный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (24-часовой формат).")

@router.callback_query(lambda c: c.data == "edit_duration")
async def edit_duration(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditPodrabotkaStates.work_duration)
    await callback.message.answer("Введите новую приблизительную продолжительность работы в часах (целое число):")
    await callback.answer()

@router.message(EditPodrabotkaStates.work_duration)
async def process_new_duration(message: types.Message, state: FSMContext):
    work_duration = message.text
    duration_pattern = r"^\d+$"
    if re.match(duration_pattern, work_duration):
        job_id_data = await state.get_data()
        job_id = job_id_data.get("edit_offer_id")
        if await update_job_data(job_id, "work_duration", work_duration, message):
            await state.set_state(EditPodrabotkaStates.menu)
            await message.answer(f"Продолжительность успешно обновлена на '{work_duration}'.")
        else:
            await message.answer(f"Не удалось обновить продолжительность для подработки с ID {job_id}.")
    else:
        await message.answer("Некорректный формат продолжительности. Пожалуйста, введите продолжительность работы в часах (целое число).")

async def update_job_data(job_id, field, new_value, message: types.Message):
    podrabotki = load_podrabotki()
    updated = False
    for i, job in enumerate(podrabotki):
        if job.get("id") == job_id:
            podrabotki[i][field] = new_value
            updated = True
            break
    if updated:
        save_podrabotki(podrabotki)
        return True
    else:
        return False