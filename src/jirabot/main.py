#!/usr/bin/env python

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import jirabot.jira.client as client
import jirabot.jira.worklogs as worklog
from jirabot.jira.worklogs import Worklog
from jirabot.log_helper import build_loger

JIRA_BOT_TELEGRAM_TOKEN = os.environ.get('JIRA_BOT_TELEGRAM_TOKEN')

# Configure logging
log = build_loger('bot', logging.INFO)

# Initialize Bot instance with default bot properties which will be passed to all API calls
try:
    bot = Bot(token=JIRA_BOT_TELEGRAM_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
except Exception as e:
    log.error(e)
    log.info('Проверте файл конфигурации бота, особенно корректность токена')
    sys.exit(-1)

dp = Dispatcher()


def summary(timetrack: int) -> tuple[int, int, int]:
    hours, remainder = divmod(timetrack, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = (int(hours), int(minutes), int(seconds))
    return result


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("status"))
async def command_status_handler(message: Message):
    jira = client.auth()
    if not jira:
        await message.reply('Не удалось авторизироваться в Jira')
        return -1

    issues = worklog.get_issues_by_user_and_week(jira=jira)
    if not issues:
        await message.reply('Задач за неделю не найдено')
        return
    worklogs: list[Worklog] = worklog.get_by_user_and_week(issues)
    timetrack = sum([w.timeSpentSeconds for w in worklogs])
    result = summary(timetrack)
    output = [
        f"Привет, {message.from_user.full_name}",
        "За последнюю неделю вы работали над:", ""
    ]
    for i in issues:
        line = f'[{i.key}]: {i.fields.summary}'
        output.append(line)
        output.append(f"{client.JIRA_SITE}/browse/{i.key}")
        output.append('')

    output.append(
        f'Залогировано: {result[0]:02d}h {result[1]:02d}m {result[2]:02d}s')
    text = '\n'.join(output)
    log.info(text)
    await message.reply(text)


async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
