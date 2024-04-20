from exam_guard.adapters.spi.repositories.monitor_data import MonitorDataRepository
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository
from infra.database.sqlalchemy.session import AbstractDatabase


class MonitorDataContainerMixin:
    db: AbstractDatabase
    monitor_data_repository: AbstractMonitorDataRepository

    def _get_monitor_data_repository(self) -> AbstractMonitorDataRepository:
        return MonitorDataRepository(self.db.create_session)
