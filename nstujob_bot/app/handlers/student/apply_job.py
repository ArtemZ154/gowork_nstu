from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from app.states.student_application import ApplyJobStates
import json
import os
import re

router = Router()
DATA_PATH_PODRABOTKI = "nstujob_bot/app/data/podrabotki.json"
DATA_PATH_USERS = "nstujob_bot/app/data/users.json"
DATA_PATH_APPLICATIONS = "nstujob_bot/app/data/applications.json"

def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} if path == DATA_PATH_USERS else []

def save_data(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

load_podrabotki = lambda: load_data(DATA_PATH_PODRABOTKI)
load_users = lambda: load_data(DATA_PATH_USERS)
load_applications = lambda: load_data(DATA_PATH_APPLICATIONS)
save_applications = lambda data: save_data(data, DATA_PATH_APPLICATIONS)

@router.callback_query(lambda c: c.data.startswith("apply_job_"))
async def start_apply_for_job(callback: types.CallbackQuery, state: FSMContext):
    podrabotka_id = int(callback.data.split("_")[2])
    await state.update_data(podrabotka_id=podrabotka_id)
    await state.set_state(ApplyJobStates.waiting_for_salary)
    await callback.message.answer("Укажите сумму, за которую вы готовы выполнить эту работу (только цифры):")
    await callback.answer()

@router.message(ApplyJobStates.waiting_for_salary)
async def process_desired_salary(message: types.Message, state: FSMContext):
    salary = message.text
    payment_pattern = r"^\d+$"
    if re.match(payment_pattern, salary):
        await state.update_data(desired_salary=salary)
        await send_application_and_notify(message, state)
    else:
        await message.answer("Пожалуйста, введите желаемую сумму оплаты цифрами.")

async def send_application_and_notify(message: types.Message, state: FSMContext):
    data = await state.get_data()
    podrabotka_id = data.get("podrabotka_id")
    desired_salary = data.get("desired_salary")
    student_id = str(message.from_user.id)

    podrabotki = load_podrabotki()
    job = next((p for p in podrabotki if p.get("id") == podrabotka_id), None)

    if not job:
        await message.answer("Предложение подработки не найдено.")
        return

    applications = load_applications()
    already_applied = any(
        app.get("student_id") == student_id and app.get("podrabotka_id") == podrabotka_id
        for app in applications
    )

    if already_applied:
        await message.answer("Вы уже откликались на эту подработку ранее.")
        return

    employer_id = str(job.get("employer_id"))
    users = load_users()
    student_info = users.get(student_id)
    employer_info = users.get(employer_id)

    if not student_info or not employer_info:
        await message.answer("Произошла ошибка при обработке отклика.")
        return

    student_full_name = student_info.get("full_name", "Не указано")
    student_contacts = student_info.get("contacts", "Не указано")
    job_title = job.get("title", "Без названия")

    notification_text = (
        f"🔔 Новый отклик на вашу подработку <b>'{job_title}'</b>!\n\n"
        f"<b>Студент:</b> {student_full_name}\n"
        f"<b>Контакты:</b> {student_contacts}\n"
        f"<b>Желаемая оплата:</b> {desired_salary}"
    )

    try:
        await message.bot.send_message(employer_id, notification_text, parse_mode="HTML")
        await message.answer(f"Ваш отклик на подработку '{job_title}' с желаемой оплатой {desired_salary} отправлен работодателю.")

        # Сохраняем информацию об отклике
        applications.append({
            "student_id": student_id,
            "podrabotka_id": podrabotka_id,
            "desired_salary": desired_salary
        })
        save_applications(applications)

    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке уведомления работодателю: {e}")

    await state.clear()