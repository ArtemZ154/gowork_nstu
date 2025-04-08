# app/handlers/__init__.py
from aiogram import Router

# Важно: Импортируем именно переменные-роутеры из соответствующих модулей/пакетов
from .common import common_router
from .admin import admin_router      # Предполагается, что в app/handlers/admin/__init__.py есть admin_router
from .employer import employer_router  # Предполагается, что в app/handlers/employer/__init__.py есть employer_router
from .student import student_router    # Предполагается, что в app/handlers/student/__init__.py есть student_router

# Создаем главный роутер уровня приложения
# Все остальные роутеры будут подключены к нему
main_router = Router(name="main_app_router")

# Подключаем роутеры в нужном порядке (если порядок важен)
# Обычно порядок подключения важен, если есть пересекающиеся фильтры/хэндлеры
main_router.include_router(common_router)
main_router.include_router(admin_router)
main_router.include_router(employer_router)
main_router.include_router(student_router)

# Теперь main_router содержит все хэндлеры из подключенных роутеров