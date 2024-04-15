from exam_guard.di.mixins import ExamGuardContainerMixin
from infra.database.sqlalchemy.session import AbstractDatabase, Database
from utils.di import DIContainer


class AppContainerMixin:
    db: AbstractDatabase

    def _get_db(self) -> AbstractDatabase:
        return Database()


class AppContainer(AppContainerMixin, ExamGuardContainerMixin, DIContainer):
    pass
