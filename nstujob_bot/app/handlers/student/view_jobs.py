# app/handlers/student/view_jobs.py
from aiogram import Router, types
from datetime import datetime, time, timedelta
from collections import defaultdict
from aiogram.fsm.context import FSMContext

import requests
import json
import os

router = Router()
DATA_PATH_PODRABOTKI = "nstujob_bot/app/data/podrabotki.json"
DATA_PATH_USERS = "nstujob_bot/app/data/users.json"

def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} if path == DATA_PATH_USERS else []

load_podrabotki = lambda: load_data(DATA_PATH_PODRABOTKI)
load_users = lambda: load_data(DATA_PATH_USERS)

# --- Функции для получения и обработки расписания ---
def get_schedule(group_id):
    try:
        response = requests.get(
            f"https://api.ciu.nstu.ru/v1.1/student/get_data/app/get_group_schedule/{group_id}",
            headers={"x-apikey": "E6E0C3AF135E3A44E0530718000A434A"},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка при запросе расписания: {str(e)}")
        return None


def should_skip_lesson(lesson):
    """Определяем, нужно ли пропустить это занятие"""
    excluded_disciplines = [
        "Основы проектной деятельности",
        "Физическая культура и спорт"
    ]
    excluded_types = ["ЛР"]

    discipline = lesson.get('DISCIPLINE_NAME', '')
    lesson_type = lesson.get('TYPE_STUDY_WORK', '')

    return discipline in excluded_disciplines or lesson_type in excluded_types


def get_day_schedule(intervals):
    """Объединяет все интервалы дня в один непрерывный"""
    if not intervals:
        return None

    start = min(i[0] for i in intervals)
    end = max(i[1] for i in intervals)

    return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"


def checkers(group_id):
    schedule_data = get_schedule(group_id)
    if not schedule_data:
        return None

    daily_schedule = defaultdict(list)
    all_dates = set()

    # Сначала собираем все даты
    if isinstance(schedule_data, list):
        for lesson in schedule_data:
            try:
                date = lesson['DAY_DATE'].split('T')[0]
                all_dates.add(date)
            except (KeyError, AttributeError):
                continue

    # Затем обрабатываем занятия
    if isinstance(schedule_data, dict):
        schedule_data = [schedule_data]

    for lesson in schedule_data or []:
        try:
            if should_skip_lesson(lesson):
                continue

            date = lesson['DAY_DATE'].split('T')[0]
            start = time.fromisoformat(lesson['START_TIME'])
            end = time.fromisoformat(lesson['END_TIME'])
            daily_schedule[date].append((start, end))
        except (KeyError, ValueError, AttributeError):
            continue

    # Формируем результат
    result = {}
    for date in sorted(all_dates):
        time_range = get_day_schedule(daily_schedule.get(date, []))
        result[date] = time_range if time_range else None

    return result

# --- Функция для проверки, пересекается ли время работы с расписанием ---
def is_work_time_conflicts_with_schedule(work_start_time_str, work_end_time_str, work_date_str, schedule):
    """
    Проверяет, пересекается ли время работы с расписанием занятий.

    Args:
        work_start_time_str (str): Начало работы в формате HH:MM.
        work_end_time_str (str): Конец работы в формате HH:MM.
        work_date_str (str): Дата работы в формате<ctrl3348>-MM-DD.
        schedule (dict): Расписание занятий, возвращаемое функцией checkers.

    Returns:
        bool: True, если время работы пересекается с расписанием, False - если нет.
    """
    if work_date_str not in schedule or schedule[work_date_str] is None:
        return False  # Нет занятий в этот день

    schedule_time_range_str = schedule[work_date_str]
    if schedule_time_range_str is None:
        return False

    schedule_start_str, schedule_end_str = schedule_time_range_str.split('-')

    try:
        work_start_time = datetime.strptime(f"{work_date_str} {work_start_time_str}", '%Y-%m-%d %H:%M')
        work_end_time = datetime.strptime(f"{work_date_str} {work_end_time_str}", '%Y-%m-%d %H:%M')
        schedule_start_time = datetime.strptime(f"{work_date_str} {schedule_start_str}", '%Y-%m-%d %H:%M')
        schedule_end_time = datetime.strptime(f"{work_date_str} {schedule_end_str}", '%Y-%m-%d %H:%M')
    except ValueError:
        print(f"Ошибка при парсинге времени: work_start={work_start_time_str}, work_end={work_end_time_str}, schedule_start={schedule_start_str}, schedule_end={schedule_end_str}, date={work_date_str}")
        return False

    # Проверяем, есть ли пересечение интервалов
    return not (work_end_time <= schedule_start_time or work_start_time >= schedule_end_time)

@router.message(lambda message: message.text and message.text.lower() == "поиск подработки")
async def view_available_jobs(message: types.Message, state: FSMContext):
    student_id = str(message.from_user.id)
    users = load_users()
    student_info = users.get(student_id)
    podrabotki = load_podrabotki()
    filtered_podrabotki = []

    if not student_info or student_info.get("role") != "student":
        await message.answer("Вы не зарегистрированы как студент.")
        return

    group_id = student_info.get("group")
    if not group_id:
        await message.answer("Не удалось определить вашу группу. Пожалуйста, обновите информацию в профиле.")
        return

    schedule = checkers(group_id)
    if schedule is None:
        await message.answer("Не удалось получить расписание. Показываю все доступные предложения подработки.")
        filtered_podrabotki_with_mobility = [offer for offer in podrabotki if not student_info.get("mobility") or offer.get("mobility_friendly")]
        if not filtered_podrabotki_with_mobility:
            await message.answer("Нет доступных предложений подработки.")
            return
        for offer in filtered_podrabotki_with_mobility:
            title = offer.get("title", "Без названия")
            description = offer.get("description", "Описание отсутствует")
            payment = offer.get("payment", "Не указано")
            offer_id = offer.get("id", "Неизвестно")

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Откликнуться", callback_data=f"apply_job_{offer_id}")
                ]
            ])

            mobility_friendly = offer.get("mobility_friendly", False)
            mobility_text = "\nДоступно для маломобильных" if mobility_friendly else ""

            text = f"<b>Название:</b> {title}\n"
            text += f"<b>Описание:</b> {description}\n"
            text += f"<b>Оплата:</b> {payment}\n"
            if mobility_text:
                text += f"<b>{mobility_text}</b>\n"

            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        return

    today = datetime.now().strftime('%Y-%m-%d')
    filtered_podrabotki_with_time = []

    for offer in podrabotki:
        if not student_info.get("mobility") or offer.get("mobility_friendly"):
            work_date_str = offer.get("work_date")
            work_time_str = offer.get("work_time")
            work_duration_str = offer.get("work_duration")

            if work_date_str and work_time_str and work_duration_str:
                if work_date_str.lower() == "сегодня":
                    work_date_str = today
                try:
                    start_time = datetime.strptime(work_time_str, "%H:%M")
                    duration = int(work_duration_str)
                    end_time = start_time + timedelta(hours=duration)
                    start_time_str = start_time.strftime("%H:%M")
                    end_time_str = end_time.strftime("%H:%M")

                    if not is_work_time_conflicts_with_schedule(start_time_str, end_time_str, work_date_str, schedule):
                        filtered_podrabotki_with_time.append(offer)
                except ValueError as e:
                    print(f"Ошибка при обработке времени для вакансии {offer.get('title')}: {e}")
                    filtered_podrabotki_with_time.append(offer) # Если ошибка с форматом времени, показываем вакансию
            else:
                filtered_podrabotki_with_time.append(offer)

    if not filtered_podrabotki_with_time:
        await message.answer("Нет доступных предложений подработки на время, свободное от учебы.")
        return

    for offer in filtered_podrabotki_with_time:
        title = offer.get("title", "Без названия")
        description = offer.get("description", "Описание отсутствует")
        payment = offer.get("payment", "Не указано")
        offer_id = offer.get("id", "Неизвестно")
        work_date_str = offer.get("work_date", "Не указано")
        work_time_str = offer.get("work_time", "Не указано")
        work_duration_str = offer.get("work_duration", "Не указано")

        if work_date_str.lower() == "сегодня":
            work_date_str = today

        start_time_display = "Не указано"
        end_time_display = "Не указано"

        if work_time_str and work_duration_str:
            try:
                start_time = datetime.strptime(work_time_str, "%H:%M")
                duration = int(work_duration_str)
                end_time = start_time + timedelta(hours=duration)
                start_time_display = start_time.strftime("%H:%M")
                end_time_display = end_time.strftime("%H:%M")
            except ValueError:
                pass

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Откликнуться", callback_data=f"apply_job_{offer_id}")
            ]
        ])

        mobility_friendly = offer.get("mobility_friendly", False)
        mobility_text = "\nДоступно для маломобильных" if mobility_friendly else ""

        text = f"<b>Название:</b> {title}\n"
        text += f"<b>Описание:</b> {description}\n"
        text += f"<b>Оплата:</b> {payment}\n"
        text += f"<b>Время:</b> {start_time_display}-{end_time_display} ({work_date_str})\n"
        if mobility_text:
            text += f"<b>{mobility_text}</b>\n"

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")