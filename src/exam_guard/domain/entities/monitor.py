from dataclasses import dataclass, field
import uuid as uuid_lib

from exam_guard.domain.entities.monitor_type import MonitorTypeEntity


@dataclass(kw_only=True)
class MonitorEntity:
    eui: uuid_lib.UUID = field(default_factory=uuid_lib.uuid4)
    monitor_type: MonitorTypeEntity
