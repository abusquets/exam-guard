from dataclasses import dataclass, field
from typing import List

from exam_guard.domain.entities.monitor import MonitorEntity


@dataclass(kw_only=True)
class MonitorRegisterEntity:
    # TODO: change to uuid, but first need to fix the database
    id: int
    monitor: MonitorEntity
    value_xpath: str
    # TODO: change to interval_to_check, but first need to fix the database
    interval: int
    threshold: float
    move_end_to: int = 0

    @property
    def interval_to_check(self) -> int:
        return self.interval


@dataclass(kw_only=True)
class StudentRegisterEntity:
    uuid: str
    student: str
    active: bool
    monitors: List[MonitorRegisterEntity] = field(default_factory=list)
