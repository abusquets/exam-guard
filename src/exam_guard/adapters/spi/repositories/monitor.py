from sqlalchemy.orm import registry, relationship

from exam_guard.adapters.spi.repositories import monitor_type  # noqa
from exam_guard.domain.entities.monitor import MonitorEntity
from exam_guard.domain.entities.monitor_type import MonitorTypeEntity
from exam_guard.domain.ports.repositories.monitor_type import AbstractMonitorTypeRepository
from exam_guard.infra.database.sqlalchemy.models import monitors
from shared.repository.sqlalchemy import SqlAlchemyReadRepository


mapper_registry = registry()

mapper_registry.map_imperatively(
    MonitorEntity,
    monitors,
    properties={
        'monitor_type': relationship(MonitorTypeEntity, lazy='joined'),
    },
)


class MonitorTypeRepository(
    SqlAlchemyReadRepository[MonitorEntity],
    AbstractMonitorTypeRepository,
):
    default_key_param = 'eui'
