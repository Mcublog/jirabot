import os


def get_env_var(variable: str) -> str:
    if (var := os.environ.get(variable)) is None:
        return ""
    return var


JIRA_BOT_TELEGRAM_TOKEN = get_env_var('JIRA_BOT_TELEGRAM_TOKEN')
USER_EMAIL = get_env_var('JIRA_EMAIL')
USER_TOKEN = get_env_var('JIRA_TOKEN')
JIRA_SITE = get_env_var('JIRA_SITE')
DB_FILENAME = "jirabot.db"
