from dataclasses import dataclass, field
import uuid as uuid_lib


@dataclass(kw_only=True)
class MonitorTypeEntity:
    uuid: uuid_lib.UUID = field(default_factory=uuid_lib.uuid4)
    name: str
    monitor_type: str
    frequency: int
