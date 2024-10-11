from jira import JIRA, exceptions

import jirabot.config as cfg


def auth() -> JIRA | None:
    try:
        jira = JIRA(cfg.JIRA_SITE, basic_auth=(cfg.USER_EMAIL, cfg.USER_TOKEN))
        jira.myself()
    except exceptions.JIRAError as e:
        print(e.text)
        return None
    return jira
