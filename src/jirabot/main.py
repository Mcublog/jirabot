#!/usr/bin/env python

import asyncio
import logging
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
import jirabot.ui.keyboard as keyboards
import jirabot.utils as utils
from jirabot.jira.worklogs import UserIssue, Worklog
from jirabot.log_helper import build_loger
from jirabot.ui.text import (ADD_COMMENT, AUTH_ERROR, BOT_CREATION_ERROR,
                             INCORRECT_ISSUE, ISSUE_NOT_FOUND_F,
                             ISSUES_BY_WEEK_NOT_FOUND, TIME_LOGGED_FAILED,
                             TIME_LOGGED_SUCCESS)

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
g_issue = UserIssue()

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
        f'Logged: {result[0]:02d}h {result[1]:02d}m {result[2]:02d}s')
    text = '\n'.join(output)
    log.info(text)
    global g_issue
    g_issue = UserIssue()
    await message.reply(text,
                        reply_markup=keyboards.issue_keyboard(issues_key))


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

    global g_issue
    g_issue.userd_id = message.from_user.id
    g_issue.issue_key = issue.key
    log.info(f"{g_issue}")

    await message.reply('\n'.join(line),
                        reply_markup=keyboards.time_spent_keyboard())


@dp.message(F.text.func(filters.worktime_filter))
async def process_worktime(message: Message):
    time_spent = message.text
    log.info(time_spent)

    global g_issue
    g_issue.work_time = message.text
    return message.answer(ADD_COMMENT)

@dp.message()
async def process_message(message: Message):
    global g_issue
    if not g_issue.is_filled():
        await message.answer(INCORRECT_ISSUE)

    if (jira := client.auth()) is None:
        return await message.answer(AUTH_ERROR)

    ret = jira.add_worklog(
        issue = g_issue.issue_key,
        timeSpent = g_issue.work_time,
        comment = message.text
    )
    # log.info(ret)
    g_issue = UserIssue()
    if isinstance(ret, Worklog):
        return await message.answer(TIME_LOGGED_SUCCESS)
    return await message.answer(TIME_LOGGED_FAILED)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    log.info("Started")
    asyncio.run(main())
