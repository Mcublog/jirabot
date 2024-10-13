import requests
from jira import JIRA, exceptions

from jirabot.states.registration import RegistationData


def auth(reg_data: RegistationData) -> JIRA | None:
    try:
        jira = JIRA(reg_data.site, basic_auth=(reg_data.email, reg_data.token))
        jira.myself()
    except exceptions.JIRAError as e:
        print(e.text)
        return None
    except requests.exceptions.MissingSchema as e:
        print(e)
        return None
    return jira
