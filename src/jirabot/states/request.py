from aiogram.fsm.state import State, StatesGroup


class JiraSqlRequestStates(StatesGroup):
    getting_jsql = State()
    getting_email = State()
    getting_token = State()
