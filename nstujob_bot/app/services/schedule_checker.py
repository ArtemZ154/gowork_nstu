import requests
import json
from datetime import datetime, time
from collections import defaultdict


def get_schedule(group_id):
    try:
        response = requests.get(
            f"https://api.ciu.nstu.ru/v1.1/student/get_data/app/get_group_schedule/{group_id}",
            headers={"x-apikey": "E6E0C3AF135E3A44E0530718000A434A"},
            timeout=0
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка при запросе: {str(e)}")
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