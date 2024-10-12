#!/usr/bin/env python

import logging

from aiogram import Router, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from jirabot.log_helper import build_loger
from jirabot.ui.text import CURRENT_VERSION_F, PROCESS_HINT
from jirabot.version import VERSION

# Configure logging
log = build_loger('other', logging.INFO)

other_router = Router()


@other_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@other_router.message(Command("version"))
async def command_version_handler(message: Message):
    await message.reply(CURRENT_VERSION_F.format(VERSION))


@other_router.message()
async def process_message(message: Message):
    await message.answer(PROCESS_HINT)
