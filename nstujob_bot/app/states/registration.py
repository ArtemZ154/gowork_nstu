# app/states/registration.py
from aiogram.fsm.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    role = State()
    student_group = State()
    student_contacts = State()
    student_full_name = State()
    student_mobility = State()
    employer_name = State()
    employer_contacts = State()
    employer_full_name = State()
    employer_inn = State()