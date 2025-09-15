from datetime import datetime, timedelta, timezone

from jira import JIRA, Issue, Worklog


def get_worklogs_by_issues(jira: JIRA, issues: list[Issue]) -> list[Worklog]:
    worklogs = []
    for i in issues:
        worklogs += jira.worklogs(issue=i.key)
    return worklogs


def by_week(worklogs: list[Worklog], account_id: str) -> list[Worklog]:
    worklogs_by_week: list[Worklog] = []
    now = datetime.now(timezone.utc).replace(hour=0,
                                             minute=0,
                                             second=0,
                                             microsecond=0)
    for w in worklogs:
        t = datetime.strptime(w.created, '%Y-%m-%dT%H:%M:%S.%f%z')
        if w.updateAuthor.accountId != account_id:
            continue
        if t < now - timedelta(days=7):
            continue
        worklogs_by_week.append(w)
    return worklogs_by_week


def get_issues_by_user_and_week(jira: JIRA) -> list[Issue]:
    issues = []
    DB_REQUEST = '''WorkLogAuthor = currentUser() and
    WorkLogDate > startOfWeek(-1) order by created desc'''
    for issue in jira.search_issues(DB_REQUEST, fields=None):
        issues.append(issue)
    return issues
