from aiogram.fsm.state import StatesGroup, State

class ApplicationStates(StatesGroup):
    """Состояния для процесса подачи заявки студентом на работу."""
    waiting_for_salary = State()  # Ожидание ввода желаемой заработной платы
    application_sent = State()    # Заявка отправлена
    application_approved = State()# Заявка одобрена работодателем
    application_rejected = State()# Заявка отклонена работодателем
    # Другие состояния, если необходимы