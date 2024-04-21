from typing import List, cast

from sqlalchemy.orm import registry, relationship

from exam_guard.adapters.spi.repositories import monitor_data  # noqa
from exam_guard.domain.entities.monitor import MonitorEntity
from exam_guard.domain.entities.student_register import MonitorRegisterEntity, StudentRegisterEntity
from exam_guard.domain.ports.repositories.student_register import (
    AbstractStudentRegisterRepository,
    StudentRegisterFilter,
)
from exam_guard.infra.database.sqlalchemy.models import monitors, students_register, students_register_monitors
from shared.repository.sqlalchemy import SqlAlchemyReadRepository


mapper_registry = registry()
mapper_registry.map_imperatively(
    MonitorRegisterEntity,
    students_register_monitors,
    properties={
        'monitor': relationship(
            MonitorEntity, lazy='joined', primaryjoin=(students_register_monitors.c.monitor_id == monitors.c.eui)
        ),
    },
)
mapper_registry.map_imperatively(
    StudentRegisterEntity,
    students_register,
    properties={
        'monitors': relationship(
            MonitorRegisterEntity,
            secondary=students_register_monitors,
            # TODO: selectin is not working, investigate alias problem
            lazy='immediate',
            secondaryjoin=(students_register_monitors.c.student_register_id == students_register.c.uuid),
        ),
    },
)


class StudentRegisterRepository(
    SqlAlchemyReadRepository[StudentRegisterEntity],
    AbstractStudentRegisterRepository,
):
    default_key_param = 'id'

    async def list_filter(self, filter_by: StudentRegisterFilter) -> List[StudentRegisterEntity]:
        ret = await self.filter_by({'active': filter_by.active})
        # TODO: typing, bad detection of TYPE_CHECKING
        return cast(List[StudentRegisterEntity], ret)
