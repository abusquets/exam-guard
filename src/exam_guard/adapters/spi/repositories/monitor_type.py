from sqlalchemy.orm import registry

from exam_guard.domain.entities.monitor_type import MonitorTypeEntity
from exam_guard.domain.ports.repositories.monitor_type import AbstractMonitorTypeRepository
from exam_guard.infra.database.sqlalchemy.models import monitor_types
from shared.repository.sqlalchemy import SqlAlchemyReadRepository


mapper_registry = registry()

mapper_registry.map_imperatively(MonitorTypeEntity, monitor_types)


class MonitorTyepeRepository(
    SqlAlchemyReadRepository[MonitorTypeEntity],
    AbstractMonitorTypeRepository,
):
    default_key_param = 'uuid'
