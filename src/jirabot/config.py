import os


def get_env_var(variable: str) -> str:
    if (var := os.environ.get(variable)) is None:
        return ""
    return var


JIRA_BOT_TELEGRAM_TOKEN = get_env_var('JIRA_BOT_TELEGRAM_TOKEN')
DB_FILENAME = "jirabot.db"
