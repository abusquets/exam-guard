from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository
from exam_guard.schemas.monitor_data import CreateMonitorDataDTO, MonitorDataInDTO


class MonitorDataService:
    def __init__(
        self,
        monitor_data_repository: AbstractMonitorDataRepository,
    ):
        self._monitor_data_repository = monitor_data_repository

    async def add_monitor_data(self, in_dto: MonitorDataInDTO) -> None:
        create_dto = CreateMonitorDataDTO(monitor_id=in_dto.eui, data=in_dto.model_dump(), ts=in_dto.ts)
        await self._monitor_data_repository.create(create_dto)
