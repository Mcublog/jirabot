#!/usr/bin/env python

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import jirabot.config as cfg
import jirabot.database.db as db
import jirabot.ui.text as text
from jirabot.dialogs.issue import issue_router
from jirabot.dialogs.other import other_router
from jirabot.dialogs.registration import reg_router
from jirabot.log_helper import build_loger

# Configure logging
log = build_loger('bot', logging.INFO)

async def main() -> None:
    try:
        bot = Bot(token=cfg.JIRA_BOT_TELEGRAM_TOKEN,
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except Exception as _:
        log.info(text.BOT_CREATION_ERROR)
        sys.exit(-1)

    db.init()

    dp = Dispatcher()
    dp.include_router(reg_router)
    dp.include_router(issue_router)
    dp.include_router(other_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    log.info("Started")
    asyncio.run(main())
