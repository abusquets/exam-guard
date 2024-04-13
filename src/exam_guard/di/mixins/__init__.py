from exam_guard.di.mixins.monitor_data import MonitorDataContainerMixin
from exam_guard.di.mixins.student_register import StudentRegisterContainerMixin


class ExamGuardContainerMixin(MonitorDataContainerMixin, StudentRegisterContainerMixin):
    pass
