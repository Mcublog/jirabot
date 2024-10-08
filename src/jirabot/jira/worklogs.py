import os
from datetime import datetime, timedelta, timezone

from jira import JIRA, Issue, Worklog


def get_issues_by_user_and_week(jira: JIRA) -> list[Issue]:
    issues = []
    for issue in jira.search_issues(
            'WorkLogAuthor = currentUser() and WorkLogDate > startOfWeek(-1) order by created desc',
    ):
        issues.append(issue)
    return issues


def get_by_user_and_week(issues: list[Issue]) -> list[Worklog]:
    worklogs = []
    for issue in issues:
        worklogs += issue.fields.worklog.worklogs

    if not worklogs:
        return []

    worklogs_by_week: list[Worklog] = []
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    for w in worklogs:
        t = datetime.fromisoformat(w.created)
        if t < now - timedelta(days=6):
            continue
        worklogs_by_week.append(w)

    return worklogs_by_week
