from aiogram.fsm.state import StatesGroup, State

class JobPostingStates(StatesGroup):
    job_type = State()
    description = State()
    salary = State()
    search_duration = State()
    # Добавьте другие состояния по мере необходимости