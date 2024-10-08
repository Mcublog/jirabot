from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_keyboard(issues: list[str]) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=k) for k in issues],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="На какую задачу записать?",
        one_time_keyboard=True)
    return keyboard
