import abc
from typing import List, Optional, Tuple
import uuid as uuid_lib

from pydantic import BaseModel

from exam_guard.domain.entities.monitor_data import MonitorDataEntity
from exam_guard.schemas.monitor_data import CreateMonitorDataDTO


class MonitorDataFilter(BaseModel):
    monitor_id: Optional[uuid_lib.UUID] = None
    ts_between: Optional[Tuple[int, int]] = None


class AbstractMonitorDataRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, monitor_data: CreateMonitorDataDTO) -> MonitorDataEntity: ...

    @abc.abstractmethod
    async def first(self, filter_by: MonitorDataFilter) -> Optional[MonitorDataEntity]: ...

    @abc.abstractmethod
    async def list_filter(self, filter_by: MonitorDataFilter) -> List[MonitorDataEntity]: ...
