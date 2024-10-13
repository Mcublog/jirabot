from dataclasses import dataclass, field

from aiogram.fsm.state import State, StatesGroup


@dataclass
class RegistationData:
    user_id: int = -1
    email: str = ""
    token: str = ""
    site: str = ""


class RegistartionStates(StatesGroup):
    getting_site = State()
    getting_email = State()
    getting_token = State()
