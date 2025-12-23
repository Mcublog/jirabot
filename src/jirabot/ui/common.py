from aiogram.types import Message
from jira import Issue

from jirabot.ui.text import GREETING_F, YOU_WORKING_WITH


def create_greetings(message: Message) -> list[str]:
    name = "Anonimus"
    if not message.from_user is None:
        name = message.from_user.full_name

    return [
        GREETING_F.format(name),
        YOU_WORKING_WITH, ""
    ]

def create_issue_names(issues: list[Issue], site: str, ) -> tuple[list[str], list[str]]:
    issues_key = []
    descriptions = []
    for i in issues:
        summary = i.fields.summary.replace("%", "%%")
        line = f'{i.key}: {summary}' # TODO: копирование в MD f'`{i.key}`: {i.fields.summary}' не работает в HTML
        descriptions.append(line)
        issues_key.append(f"{i.key}")
        descriptions.append(f"{site}/browse/{i.key}")
        descriptions.append('')
    return issues_key, descriptions
