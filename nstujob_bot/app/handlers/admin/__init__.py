# app/handlers/admin/__init__.py
from aiogram import Router

# Импортируем роутеры из каждого модуля админских функций
# Предполагаем, что в каждом .py файле есть переменная 'router = Router()'
from . import verification, user_management, job_management, complaints

# Создаем единый роутер для всех админских команд
admin_router = Router(name="admin_features")

admin_router.include_router(verification.router)
admin_router.include_router(user_management.router)
admin_router.include_router(job_management.router)
admin_router.include_router(complaints.router)