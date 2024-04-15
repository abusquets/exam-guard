from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class MonitorDataInDTO(BaseModel):
    model_config = ConfigDict(extra='allow')

    eui: str
    ts: int


class CreateMonitorDataDTO(BaseModel):
    monitor_id: str
    data: Dict[str, Any]
    ts: int


class UpdatePartialMonitorDataDTO(BaseModel):
    pass
