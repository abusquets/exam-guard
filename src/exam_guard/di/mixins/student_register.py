from exam_guard.adapters.spi.repositories.student_register import StudentRegisterRepository
from exam_guard.domain.ports.repositories.student_register import AbstractStudentRegisterRepository
from infra.database.sqlalchemy.session import AbstractDatabase


class StudentRegisterContainerMixin:
    db: AbstractDatabase
    student_register_repository: AbstractStudentRegisterRepository

    def _get_student_register_repository(self) -> AbstractStudentRegisterRepository:
        return StudentRegisterRepository(self.db.create_session)
