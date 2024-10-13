"""
Registration new user
"""

import logging
from dataclasses import asdict

from aiogram import Router, html
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import jirabot.database.db as db
import jirabot.jira.client as client
from jirabot.log_helper import build_loger
from jirabot.states.registration import RegistartionStates, RegistationData

# Configure logging
log = build_loger('reg', logging.INFO)

reg_router = Router()


@reg_router.message(CommandStart(), StateFilter(None))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData()
    reg_data.user_id = message.from_user.id
    await message.answer(f"""Привет, {html.bold(message.from_user.full_name)}
Для работы мне потребуются некоторые данные:
    * Домен вашей Jira например: https://yourcomanyname.atlassian.net
    * Email к которому привязан Jira аккаунт
    * Токен дял достпупа к Jira API: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
    """)
    await message.answer("Введите домен Jira")
    await state.set_state(RegistartionStates.getting_site)
    await state.set_data(asdict(reg_data))


@reg_router.message(StateFilter(RegistartionStates.getting_site))
async def site_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.site = message.text
    await state.set_data(asdict(reg_data))
    await state.set_state(RegistartionStates.getting_email)
    await message.answer("Введите Ваш Jira email")


@reg_router.message(StateFilter(RegistartionStates.getting_email))
async def email_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.email = message.text
    await state.set_data(asdict(reg_data))
    await state.set_state(RegistartionStates.getting_token)
    await message.answer("Введите Ваш Jira токен")


@reg_router.message(StateFilter(RegistartionStates.getting_token))
async def token_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.token = message.text

    db.add_user(reg_data)
    reg_data = db.get_reg_date_by_user_id(reg_data.user_id)

    await state.clear()
    await state.set_data(asdict(RegistationData()))

    if client.auth(email=reg_data.email,
                   token=reg_data.token,
                   site=reg_data.site) is None:
        return await message.answer(
            "Не удалось авторизирвоаться в Jira API, проверти свои данные и попробуйте ввести из снова"
        )

    await message.answer("Отлично вы зарегистровались")
