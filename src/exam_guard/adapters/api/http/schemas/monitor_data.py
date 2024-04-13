from pydantic import BaseModel, ConfigDict


class MonitorDataRequestDTO(BaseModel):
    model_config = ConfigDict(extra='allow')

    eui: str
    ts: int
