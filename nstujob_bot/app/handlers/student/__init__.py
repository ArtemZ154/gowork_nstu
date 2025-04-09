# app/handlers/admin/__init__.py
from aiogram import Router

# Импортируем роутеры из каждого модуля админских функций
# Предполагаем, что в каждом .py файле есть переменная 'router = Router()'
from . import view_applications, registration, profile, view_jobs, apply_job

# Создаем единый роутер для всех команд работодателя
student_router = Router(name="student_features")

student_router.include_router(view_applications.router)
student_router.include_router(registration.router)
student_router.include_router(profile.router)
student_router.include_router(view_jobs.router)
student_router.include_router(apply_job.router)
