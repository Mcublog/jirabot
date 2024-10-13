from jira import JIRA, exceptions

import jirabot.config as cfg


def auth(email: str = cfg.USER_EMAIL,
         token: str = cfg.USER_TOKEN,
         site: str = cfg.JIRA_SITE) -> JIRA | None:
    try:
        jira = JIRA(site, basic_auth=(email, token))
        jira.myself()
    except exceptions.JIRAError as e:
        print(e.text)
        return None
    return jira
