import abc
from typing import List, Optional

from pydantic import BaseModel

from exam_guard.domain.entities.student_register import StudentRegisterEntity


class StudentRegisterFilter(BaseModel):
    heart_reate: Optional[str] = None
    active: Optional[bool] = True


class AbstractStudentRegisterRepository(abc.ABC):
    @abc.abstractmethod
    async def list_filter(self, filter_by: StudentRegisterFilter) -> List[StudentRegisterEntity]: ...
