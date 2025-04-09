from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(user_role: str) -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру в зависимости от роли пользователя."""
    keyboard_buttons = []

    if user_role == "student":
        keyboard_buttons.append([
            KeyboardButton(text="Поиск подработки")
        ])
        keyboard_buttons.append([
            KeyboardButton(text="Мои отклики")
        ])
    elif user_role == "employer":
        keyboard_buttons.append([
            KeyboardButton(text="Добавить подработку")
        ])
        keyboard_buttons.append([
            KeyboardButton(text="Мои предложения") # Реализуем позже
        ])
        keyboard_buttons.append([
            KeyboardButton(text="Просмотр откликов") # Реализуем позже
        ])
    elif user_role == "admin":
        keyboard_buttons.append([
            KeyboardButton(text="Админ-панель") # Реализуем позже
        ])

    keyboard_buttons.append([
        KeyboardButton(text="Профиль") # Реализуем позже
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)