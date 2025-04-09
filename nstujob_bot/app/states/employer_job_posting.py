from aiogram.fsm.state import StatesGroup, State

class AddPodrabotkaStates(StatesGroup):
    title = State()
    description = State()
    payment = State()
    mobility_friendly = State()
    work_date = State()
    work_time = State()
    work_duration = State()
    contact_info = State()
    confirm = State()

class EditPodrabotkaStates(StatesGroup):
    menu = State()
    title = State()
    description = State()
    payment = State()
    contact_info = State()
    work_date = State()
    work_time = State()
    work_duration = State()