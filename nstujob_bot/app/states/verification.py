from aiogram.fsm.state import StatesGroup, State

class VerificationStates(StatesGroup):
    """Состояния для процесса верификации."""
    student_verification_document = State()  # Ожидание студенческого билета
    employer_verification_document = State() # Ожидание паспорта
    verification_pending = State()         # Состояние ожидания подтверждения администратором
    verification_approved = State()        # Верификация одобрена
    verification_rejected = State()        # Верификация отклонена
    # Другие состояния, если необходимы