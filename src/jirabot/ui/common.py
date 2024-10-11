import jira.config as cfg
from aiogram.types import Message
from jira import Issue

import jirabot.config as cfg
from jirabot.ui.text import GREETING_F, YOU_WORKING_WITH


def create_greetings(message: Message) -> list[str]:
    name = "Anonimus"
    if not message.from_user is None:
        name = message.from_user.full_name

    return [
        GREETING_F.format(name),
        YOU_WORKING_WITH, ""
    ]

def create_issue_names(issues: list[Issue]) -> tuple[list[str], list[str]]:
    issues_key = []
    descriptions = []
    for i in issues:
        line = f'[{i.key}]: {i.fields.summary}'
        descriptions.append(line)
        issues_key.append(i.key)
        descriptions.append(f"{cfg.JIRA_SITE}/browse/{i.key}")
        descriptions.append('')
    return issues_key, descriptions