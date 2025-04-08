from aiogram.fsm.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    role_choice = State()
    student_group = State()
    employer_inn = State()
    employer_name = State()