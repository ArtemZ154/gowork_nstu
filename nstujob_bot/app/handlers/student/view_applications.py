# app/handlers/student/view_applications.py
from aiogram import Router, types
import json
import os

router = Router()
DATA_PATH_APPLICATIONS = "nstujob_bot/app/data/applications.json"
DATA_PATH_PODRABOTKI = "nstujob_bot/app/data/podrabotki.json"

def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

load_applications = lambda: load_data(DATA_PATH_APPLICATIONS)
load_podrabotki = lambda: load_data(DATA_PATH_PODRABOTKI)

@router.message(lambda message: message.text and message.text.lower() == "мои отклики")

async def view_student_applications(message: types.Message):
    student_id = str(message.from_user.id)
    applications = load_applications()
    student_applications = [
        app for app in applications if app.get("student_id") == student_id
    ]

    if not student_applications:
        await message.answer("Вы пока не откликались ни на одну подработку.")
        return

    podrabotki = load_podrabotki()
    applied_jobs = []
    for app in student_applications:
        podrabotka_id = app.get("podrabotka_id")
        job = next((p for p in podrabotki if p.get("id") == podrabotka_id), None)
        if job:
            applied_jobs.append(job)

    if not applied_jobs:
        await message.answer("Произошла ошибка при получении информации о ваших откликах.")
        return

    text = "<b>Ваши отклики:</b>\n\n"
    for job in applied_jobs:
        title = job.get("title", "Без названия")
        description = job.get("description", "Описание отсутствует")
        payment = job.get("payment", "Не указано")
        job_id = job.get("id", "Неизвестно")
        text += f"<b>ID:</b> {job_id}\n"
        text += f"<b>Название:</b> {title}\n"
        text += f"<b>Описание:</b> {description[:50]}...\n" # Краткое описание
        text += f"<b>Оплата:</b> {payment}\n\n"

    await message.answer(text, parse_mode="HTML")