from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid as uuid_lib

from exam_guard.domain.entities.value_objects import MonitorDataId


@dataclass(kw_only=True)
class MonitorDataEntity:
    id: Optional[MonitorDataId] = None
    monitor_id: uuid_lib.UUID = field(default_factory=uuid_lib.uuid4)
    data: Dict[str, Any]
    ts: int
    created_at: Optional[datetime] = None
