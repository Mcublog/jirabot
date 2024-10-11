from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from jirabot.ui.text import HOW_MUCH_TIME_DID_IT_TAKE, WHAT_TASK_SHOULD_I_TRACK


def _keyboard(placeholder: str, button_text: list[str]) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=t) for t in button_text],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   input_field_placeholder=placeholder,
                                   one_time_keyboard=True)
    return keyboard


def issue_keyboard(issues: list[str]) -> ReplyKeyboardMarkup:
    return _keyboard(WHAT_TASK_SHOULD_I_TRACK, issues)


def time_spent_keyboard() -> ReplyKeyboardMarkup:
    TIME_SPENT_LIST = ['1d', '4h', '1h']
    return _keyboard(HOW_MUCH_TIME_DID_IT_TAKE, TIME_SPENT_LIST)
