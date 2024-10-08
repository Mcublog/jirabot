#!/usr/bin/env python

import os

from jira import JIRA

USER_EMAIL = os.environ.get('JIRA_EMAIL')
USER_TOKEN = os.environ.get('JIRA_TOKEN')


def main():
    jira = JIRA('https://crystals.atlassian.net', basic_auth=(USER_EMAIL, USER_TOKEN))
    issue = jira.issue('KKT-1090')
    print(issue.fields.description)
    for w in issue.fields.worklog.worklogs:
        print("-" * 15)
        print(w.created)
        print(w.timeSpent)
        print(w.comment)
        print("-" * 15)

if __name__ == "__main__":
    main()
