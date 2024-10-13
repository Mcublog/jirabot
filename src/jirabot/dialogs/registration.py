"""
Registration new user
"""

import logging
from dataclasses import asdict

from aiogram import Router, html
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import jirabot.database.db as db
import jirabot.jira.client as client
import jirabot.ui.text as text
from jirabot.log_helper import build_loger
from jirabot.states.registration import RegistartionStates, RegistationData

# Configure logging
log = build_loger('reg', logging.INFO)

reg_router = Router()


@reg_router.message(CommandStart(), StateFilter(None))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData()
    reg_data.user_id = message.from_user.id
    await message.answer(
        text.INFO_FOR_REGISTRATION_F.format(
            html.bold(message.from_user.full_name)))
    await message.answer(text.GET_JIRA_SITE)
    await state.set_state(RegistartionStates.getting_site)
    await state.set_data(asdict(reg_data))


@reg_router.message(StateFilter(RegistartionStates.getting_site))
async def site_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.site = message.text
    await state.set_data(asdict(reg_data))
    await state.set_state(RegistartionStates.getting_email)
    await message.answer(text.GET_JIRA_EMAIL)


@reg_router.message(StateFilter(RegistartionStates.getting_email))
async def email_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.email = message.text
    await state.set_data(asdict(reg_data))
    await state.set_state(RegistartionStates.getting_token)
    await message.answer(text.GET_JIRA_TOKEN)


@reg_router.message(StateFilter(RegistartionStates.getting_token))
async def token_handler(message: Message, state: FSMContext) -> None:
    reg_data = RegistationData(**await state.get_data())
    reg_data.token = message.text

    db.add_user(reg_data)
    reg_data = db.get_reg_date_by_user_id(reg_data.user_id)

    await state.clear()

    if client.auth(reg_data) is None:
        db.delete_by_user_id(reg_data.user_id)
        await message.answer(text.CREDENTIAL_ERROR)
        return
    log.info(f"user {message.from_user.id} added")
    await message.answer(text.CREDENTIAL_OK)


@reg_router.message(Command("stop"), StateFilter(None))
async def stop_handler(message: Message, state: FSMContext) -> None:
    if not db.get_reg_date_by_user_id(message.from_user.id):
        await message.answer(text.TRY_DELETE_NOT_REG_USER)
    else:
        db.delete_by_user_id(message.from_user.id)
        log.info(f"user {message.from_user.id} removed")
        await message.answer(text.ON_DELETE_USER)
    await state.clear()
