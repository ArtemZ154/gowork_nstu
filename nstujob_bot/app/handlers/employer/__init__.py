# app/handlers/admin/__init__.py
from aiogram import Router

# Импортируем роутеры из каждого модуля админских функций
# Предполагаем, что в каждом .py файле есть переменная 'router = Router()'
from . import applicant_selection, job_posting, view_jobs, registration

# Создаем единый роутер для всех команд работодателя
employer_router = Router(name="employer_features")

employer_router.include_router(applicant_selection.router)
employer_router.include_router(job_posting.router)
employer_router.include_router(view_jobs.router)
employer_router.include_router(registration.router)