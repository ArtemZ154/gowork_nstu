from aiogram.fsm.state import StatesGroup, State

class ApplyJobStates(StatesGroup):
    waiting_for_salary = State()