from dataclasses import dataclass, field

from aiogram.fsm.state import State, StatesGroup


@dataclass
class IssueData:
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

class LogIssue(StatesGroup):
    choosing_issue_key = State()
    choosing_work_time = State()
    choosing_comment = State()
