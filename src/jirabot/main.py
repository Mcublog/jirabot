#!/usr/bin/env python

import os
from datetime import datetime, timedelta, timezone

from jira import JIRA, Worklog, exceptions

USER_EMAIL = os.environ.get('JIRA_EMAIL')
USER_TOKEN = os.environ.get('JIRA_TOKEN')
JIRA_SITE = os.environ.get('JIRA_SITE')


def summary_print(timetrack: int):
    hours, remainder = divmod(timetrack, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(
        f"Summary: {int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s")


def get_worklogs_by_user_and_week(jira: JIRA) -> list[Worklog]:
    worklogs = []
    for issue in jira.search_issues(
            'WorkLogAuthor = currentUser() and WorkLogDate > startOfWeek(-1) order by created desc',
    ):
        print('{}: {}'.format(issue.key, issue.fields.summary))
        worklogs += issue.fields.worklog.worklogs

    if not worklogs:
        print("worklogs is empty")
        return []

    worklogs_by_week: list[Worklog] = []
    for w in worklogs:
        t = datetime.fromisoformat(w.created)
        if t < datetime.now(timezone.utc) - timedelta(days=6):
            continue
        worklogs_by_week.append(w)

    return worklogs_by_week


def main():
    try:
        jira = JIRA(JIRA_SITE, basic_auth=(USER_EMAIL, USER_TOKEN))
        jira.myself()
    except exceptions.JIRAError as e:
        print(e.text)
        return -1

    worklogs = get_worklogs_by_user_and_week(jira=jira)

    timetrack = sum([w.timeSpentSeconds for w in worklogs])

    summary_print(timetrack)


if __name__ == "__main__":
    main()
