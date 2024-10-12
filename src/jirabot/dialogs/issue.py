#!/usr/bin/env python

import logging
from dataclasses import asdict

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import jirabot.jira.client as client
import jirabot.jira.worklogs as worklog
import jirabot.ui.common as ui_common
import jirabot.ui.filters as filters
import jirabot.ui.keyboard as keyboards
import jirabot.utils as utils
from jirabot.jira.worklogs import UserIssue, Worklog
from jirabot.log_helper import build_loger
from jirabot.ui.text import (ADD_COMMENT, AUTH_ERROR, INCORRECT_ISSUE,
                             INCORRECT_WORKTIME, ISSUE_NOT_FOUND_F,
                             ISSUES_BY_WEEK_NOT_FOUND, TIME_LOGGED_FAILED,
                             TIME_LOGGED_SUCCESS)

# Configure logging
log = build_loger('issue', logging.INFO)

issue_router = Router()


class LogIssue(StatesGroup):
    choosing_issue_key = State()
    choosing_work_time = State()
    choosing_comment = State()


@issue_router.message(StateFilter(None), Command("status"))
async def command_status_handler(message: Message, state: FSMContext):
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

    await message.answer(text,
                         reply_markup=keyboards.issue_keyboard(issues_key))
    await state.set_state(LogIssue.choosing_issue_key)
    await state.set_data(asdict(UserIssue()))


@issue_router.message(LogIssue.choosing_issue_key,
                     F.text.func(filters.issue_filter))
async def process_find_word(message: Message, state: FSMContext):
    jira = client.auth()
    if not message.text or not jira:
        await message.answer(AUTH_ERROR)
        return
    if (issue := jira.issue(message.text)) is None:
        await message.answer(ISSUE_NOT_FOUND_F.format(message.text))
        return
    line = [f"[{message.text}]: {issue.fields.summary}"]

    await message.reply('\n'.join(line),
                        reply_markup=keyboards.time_spent_keyboard())
    current_issue = UserIssue(**await state.get_data())
    current_issue.userd_id = message.from_user.id
    current_issue.issue_key = issue.key
    await state.set_data(asdict(current_issue))
    # log.info(f"{current_issue}")
    await state.set_state(LogIssue.choosing_work_time)


@issue_router.message(LogIssue.choosing_work_time,
                     F.text.func(filters.worktime_filter))
async def process_worktime(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(INCORRECT_WORKTIME)
        return

    time_spent = message.text
    log.info(time_spent)

    current_issue = UserIssue(**await state.get_data())
    current_issue.work_time = message.text
    await state.set_data(asdict(current_issue))

    await message.answer(ADD_COMMENT)
    await state.set_state(LogIssue.choosing_comment)


@issue_router.message(LogIssue.choosing_comment)
async def process_comment(message: Message, state: FSMContext):

    current_issue = UserIssue(**await state.get_data())
    log.info(f"{current_issue}")
    if not current_issue.is_filled():
        return await message.answer(INCORRECT_ISSUE)

    if (jira := client.auth()) is None:
        return await message.answer(AUTH_ERROR)

    ret = jira.add_worklog(issue=current_issue.issue_key,
                           timeSpent=current_issue.work_time,
                           comment=message.text)
    # log.info(ret)
    # g_issue = UserIssue()
    answer = TIME_LOGGED_SUCCESS if isinstance(ret,
                                               Worklog) else TIME_LOGGED_FAILED
    await message.answer(answer)
    await state.clear()
    await state.set_data(asdict(UserIssue()))


