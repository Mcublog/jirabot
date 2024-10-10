#!/usr/bin/env python

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import jirabot.config as cfg
import jirabot.jira.client as client
import jirabot.jira.worklogs as worklog
import jirabot.ui.common as ui_common
import jirabot.ui.filters as filters
import jirabot.utils as utils
from jirabot.jira.worklogs import Worklog
from jirabot.log_helper import build_loger
from jirabot.ui.keyboard import build_keyboard
from jirabot.ui.text import (AUTH_ERROR, BOT_CREATION_ERROR,
                             HOW_MUCH_TIME_DID_IT_TAKE, INCORRECT_ISSUE,
                             ISSUE_NOT_FOUND_F, ISSUES_BY_WEEK_NOT_FOUND)

# Configure logging
log = build_loger('bot', logging.INFO)

# Initialize Bot instance with default bot properties which will be passed to all API calls
try:
    bot = Bot(token=cfg.JIRA_BOT_TELEGRAM_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
except Exception as e:
    log.info(BOT_CREATION_ERROR)
    sys.exit(-1)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("status"))
async def command_status_handler(message: Message):
    jira = client.auth()
    if not jira:
        await message.reply(AUTH_ERROR)
        return -1

    issues = worklog.get_issues_by_user_and_week(jira=jira)
    if not issues:
        await message.reply(ISSUES_BY_WEEK_NOT_FOUND)
        return
    worklogs: list[Worklog] = worklog.get_by_user_and_week(issues)
    timetrack = sum([w.timeSpentSeconds for w in worklogs])
    result = utils.summary(timetrack)
    output = ui_common.create_greetings(message)
    issues_key, descriptions = ui_common.create_issue_names(issues)
    output += descriptions
    output.append(
        f'Залогировано: {result[0]:02d}h {result[1]:02d}m {result[2]:02d}s')
    text = '\n'.join(output)
    log.info(text)

    await message.reply(text, reply_markup=build_keyboard(issues_key))


@dp.message(F.text.func(filters.issue_filter))
async def process_find_word(message: Message):
    jira = client.auth()
    if not message.text or not jira:
        await message.answer(AUTH_ERROR)
        return
    if (issue := jira.issue(message.text)) is None:
        await message.answer(ISSUE_NOT_FOUND_F.format(message.text))
        return
    line = [f"[{message.text}]: {issue.fields.summary}"]
    line.append(HOW_MUCH_TIME_DID_IT_TAKE)
    await message.answer('\n'.join(line))


@dp.message()
async def process_message(message: Message):
    await message.answer(INCORRECT_ISSUE)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    log.info("Started")
    asyncio.run(main())
