"""
Issue time logging FSM stuff
"""

import logging
from dataclasses import asdict

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import jirabot.database.db as db
import jirabot.jira.client as client
import jirabot.jira.worklogs as worklog
import jirabot.ui.common as ui_common
import jirabot.ui.filters as filters
import jirabot.ui.keyboard as keyboards
import jirabot.ui.text as uitext
import jirabot.utils as utils
from jirabot.jira.worklogs import Worklog
from jirabot.log_helper import build_loger
from jirabot.states.issue import IssueData, LogIssue
from jirabot.states.registration import RegistationData

# Configure logging
log = build_loger('issue', logging.INFO)

issue_router = Router()


def jira_auth_by_user_id(
        user_id: int
) -> tuple[client.JIRA | None, RegistationData | None, str]:
    if (reg := db.get_reg_date_by_user_id(user_id)) is None:
        return None, None, uitext.PLEASE_REGISTRATION

    jira = client.auth(reg)
    if not jira:
        return None, None, uitext.AUTH_ERROR

    return jira, reg, ""

@issue_router.message(
    StateFilter(None, LogIssue.choosing_issue_key,
                LogIssue.choosing_work_time), Command("status"))
async def command_status_handler(message: Message, state: FSMContext):

    jira, reg, msg = jira_auth_by_user_id(message.from_user.id)
    if not jira or not reg:
        await message.reply(msg)
        return

    issues = worklog.get_issues_by_user_and_week(jira=jira)
    if not issues:
        await message.reply(uitext.ISSUES_BY_WEEK_NOT_FOUND)
        return

    worklogs: list[Worklog] = worklog.get_worklogs_by_issues(jira, issues)
    worklogs = worklog.by_week(worklogs, jira.myself()['accountId'])
    timetrack = sum([w.timeSpentSeconds for w in worklogs])
    result = utils.summary(timetrack)
    output = ui_common.create_greetings(message)
    if issue_dict := await state.get_data():
        current_issue = IssueData(**issue_dict)
    else:
        current_issue = IssueData()
    current_issue.issues, descriptions = ui_common.create_issue_names(
        issues, reg.site)
    output += descriptions
    output.append(
        f'Logged: {result[0]:02d}h {result[1]:02d}m {result[2]:02d}s')
    text = '\n'.join(output)
    log.info(text)

    await message.answer(text,
                         parse_mode="Markdown",
                         reply_markup=keyboards.issue_keyboard(
                             current_issue.issues))
    await state.set_state(LogIssue.choosing_issue_key)
    await state.set_data(asdict(current_issue))


@issue_router.message(StateFilter(None, LogIssue.choosing_issue_key),
                      F.text.func(filters.issue_filter))
async def process_find_word(message: Message, state: FSMContext):

    jira, reg, msg = jira_auth_by_user_id(message.from_user.id)
    if not jira or not reg or not message.text:
        await message.reply(msg)
        return

    try:
        if (issue := jira.issue(message.text)) is None:
            await message.answer(uitext.ISSUE_NOT_FOUND_F.format(message.text))
            return
    except client.exceptions.JIRAError as e:
        await message.answer(
            uitext.ISSUE_NOT_FOUND_F.format(message.text) + "\r\n" + e.text)
        return

    line = [f"[{message.text}]: {issue.fields.summary}"]

    await message.reply('\n'.join(line),
                        reply_markup=keyboards.time_spent_keyboard())
    current_issue = IssueData(**await state.get_data())
    current_issue.userd_id = message.from_user.id
    current_issue.issue_key = issue.key
    await state.set_data(asdict(current_issue))
    # log.info(f"{current_issue}")
    await state.set_state(LogIssue.choosing_work_time)


@issue_router.message(LogIssue.choosing_issue_key)
async def incorrect_issue_handler(message: Message, state: FSMContext):
    current_issue = IssueData(**await state.get_data())
    await message.reply(uitext.INCORRECT_ISSUE,
                        reply_markup=keyboards.issue_keyboard(
                            current_issue.issues))


@issue_router.message(LogIssue.choosing_work_time,
                      F.text.func(filters.worktime_filter))
async def process_worktime(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(uitext.INCORRECT_WORKTIME)
        return

    time_spent = message.text
    log.info(time_spent)

    current_issue = IssueData(**await state.get_data())
    current_issue.work_time = message.text
    await state.set_data(asdict(current_issue))

    await message.answer(uitext.ADD_COMMENT)
    await state.set_state(LogIssue.choosing_comment)


@issue_router.message(LogIssue.choosing_work_time)
async def incorrect_worktime_hanlder(message: Message):
    await message.reply(uitext.INCORRECT_WORKTIME,
                        reply_markup=keyboards.time_spent_keyboard())


@issue_router.message(LogIssue.choosing_comment)
async def process_comment(message: Message, state: FSMContext):

    current_issue = IssueData(**await state.get_data())
    log.info(f"{current_issue}")
    if not current_issue.is_filled():
        return await message.answer(uitext.INCORRECT_ISSUE)

    jira, reg, msg = jira_auth_by_user_id(message.from_user.id)
    if not jira or not reg or not message.text:
        await message.reply(msg)
        return

    try:
        ret = jira.add_worklog(issue=current_issue.issue_key,
                               timeSpent=current_issue.work_time,
                               comment=message.text)
    except Exception as e:
        log.error(e)
        ret = None
    answer = uitext.TIME_LOGGED_SUCCESS if isinstance(
        ret, Worklog) else uitext.TIME_LOGGED_FAILED
    await message.answer(answer)
    await state.clear()
