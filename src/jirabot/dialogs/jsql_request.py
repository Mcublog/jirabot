"""
Custom jsql request
"""

import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from jira import JIRA, Issue, JIRAError

import jirabot.ui.common as ui_common
import jirabot.ui.text as text
from jirabot.dialogs.issue import jira_auth_by_user_id
from jirabot.log_helper import build_loger
from jirabot.states.request import JiraSqlRequestStates

# Configure logging
log = build_loger('jsql', logging.INFO)

jsql_router = Router()


def get_issues_by_custom_request(jira: JIRA, request: str) -> tuple[list[Issue], str]:
    issues = []
    try:
        for issue in jira.search_issues(request, fields=None):
            issues.append(issue)
    except JIRAError as e:
        log.error(e)
        return [], e.text
    except Exception as e:
        log.error(e)
    return issues, ""


@jsql_router.message(Command("jsql"), StateFilter(None))
async def command_jsql_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(JiraSqlRequestStates.getting_jsql)
    await message.reply(text.GET_JIRA_SQL_REQUEST)


@jsql_router.message(StateFilter(JiraSqlRequestStates.getting_jsql))
async def process_jsql(message: Message, state: FSMContext) -> None:
    await state.clear()

    if not (jsql_req := message.text):
        await message.reply("Запрос пустой")
        return

    jira, reg, msg = jira_auth_by_user_id(message.from_user.id)
    if not jira or not reg:
        await message.reply(msg)
        return

    issues, err_text = get_issues_by_custom_request(jira=jira, request=jsql_req)
    if err_text:
        await message.reply(err_text, parse_mode="Markdown")
        return

    if not issues:
        await message.reply(text.JIRA_SQL_CUSTOM_REQUEST_EXECUTE_EMTY)
        return

    _, descriptions = ui_common.create_issue_names(issues, reg.site)
    for issue in issues:
        log.info(issue.key)

    await message.reply('\n'.join(descriptions), parse_mode="Markdown")
