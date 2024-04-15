from typing import List, Optional, cast

from sqlalchemy.orm import registry

from exam_guard.domain.entities.monitor_data import MonitorDataEntity
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository, MonitorDataFilter
from exam_guard.infra.database.sqlalchemy.models import monitor_data
from exam_guard.schemas.monitor_data import CreateMonitorDataDTO, UpdatePartialMonitorDataDTO
from shared.repository.sqlalchemy import SqlAlchemyRepository


mapper_registry = registry()

mapper_registry.map_imperatively(MonitorDataEntity, monitor_data)


class MonitorDataRepository(
    SqlAlchemyRepository[MonitorDataEntity, CreateMonitorDataDTO, UpdatePartialMonitorDataDTO],
    AbstractMonitorDataRepository,
):
    default_key_param = 'id'

    async def first(self, filter_by: MonitorDataFilter) -> Optional[MonitorDataEntity]:
        filter_data = filter_by.model_dump(exclude_unset=True)
        filter_data.pop('ts_between', None)
        # TODO: implement order_by parameter
        query = self._filter_by(filter_data).order_by(monitor_data.c.ts.asc())
        async with self.session_factory() as session:
            if ret := (await session.scalars(query)).first():
                # TODO: typing, bad detection of TYPE_CHECKING
                return cast(MonitorDataEntity, ret)
            return None

    async def list_filter(self, filter_by: MonitorDataFilter) -> List[MonitorDataEntity]:
        filter_data = filter_by.model_dump(exclude_unset=True)
        ts_between = filter_data.pop('ts_between', None)
        # TODO: implement order_by parameter
        query = self._filter_by(filter_data).order_by(monitor_data.c.ts.asc())
        if ts_between:
            query = query.filter(monitor_data.c.ts.between(*ts_between))
        async with self.session_factory() as session:
            ret = (await session.scalars(query)).all()
            # TODO: typing, bad detection of TYPE_CHECKING
            return cast(List[MonitorDataEntity], ret)
