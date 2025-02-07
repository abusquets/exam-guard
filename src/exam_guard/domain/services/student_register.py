from typing import List

from exam_guard.domain.entities.student_register import StudentRegisterEntity
from exam_guard.domain.ports.repositories.student_register import (
    AbstractStudentRegisterRepository,
    StudentRegisterFilter,
)


class StudentRegisterService:
    def __init__(
        self,
        student_register_repository: AbstractStudentRegisterRepository,
    ):
        self._student_register_repository = student_register_repository

    async def curentlly_active_students(self) -> List[StudentRegisterEntity]:
        filter_by = StudentRegisterFilter(active=True)
        return await self._student_register_repository.list_filter(filter_by)
