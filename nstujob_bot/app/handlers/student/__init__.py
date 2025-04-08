# app/handlers/admin/__init__.py
from aiogram import Router

# Импортируем роутеры из каждого модуля админских функций
# Предполагаем, что в каждом .py файле есть переменная 'router = Router()'
from . import view_applications, job_search, registration

# Создаем единый роутер для всех команд работодателя
student_router = Router(name="student_features")

student_router.include_router(view_applications.router)
student_router.include_router(registration.router)
student_router.include_router(job_search.router)