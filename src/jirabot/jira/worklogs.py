from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from jira import JIRA, Issue, Worklog


@dataclass
class UserIssue:
    userd_id: int = -1
    issue_key: str = ""
    work_time: str = ""
    issues: list[str] = field(default_factory=list)

    def is_filled(self) -> bool:
        if self.userd_id == -1:
            return False
        if not self.issue_key:
            return False
        if not self.work_time:
            return False
        return True

def get_issues_by_user_and_week(jira: JIRA) -> list[Issue]:
    issues = []
    DB_REQUEST = '''WorkLogAuthor = currentUser() and
    WorkLogDate > startOfWeek(-1) order by created desc'''
    for issue in jira.search_issues(DB_REQUEST, ):
        issues.append(issue)
    return issues


def get_by_user_and_week(issues: list[Issue]) -> list[Worklog]:
    worklogs = []
    for issue in issues:
        worklogs += issue.fields.worklog.worklogs

    if not worklogs:
        return []

    worklogs_by_week: list[Worklog] = []
    now = datetime.now(timezone.utc).replace(hour=0,
                                             minute=0,
                                             second=0,
                                             microsecond=0)
    for w in worklogs:
        t = datetime.fromisoformat(w.created).replace(hour=0,
                                                      minute=0,
                                                      second=0,
                                                      microsecond=0)
        if t < now - timedelta(days=7):
            continue
        worklogs_by_week.append(w)

    return worklogs_by_week
