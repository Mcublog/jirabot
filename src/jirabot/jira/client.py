import os

from jira import JIRA, exceptions

USER_EMAIL = os.environ.get('JIRA_EMAIL')
USER_TOKEN = os.environ.get('JIRA_TOKEN')
JIRA_SITE = os.environ.get('JIRA_SITE')

def auth() -> JIRA | None:
    try:
        jira = JIRA(JIRA_SITE, basic_auth=(USER_EMAIL, USER_TOKEN))
        jira.myself()
    except exceptions.JIRAError as e:
        print(e.text)
        return None
    return jira
