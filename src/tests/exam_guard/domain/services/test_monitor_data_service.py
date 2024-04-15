import time
from unittest.mock import AsyncMock
import uuid as uuid_lib

import pytest

from exam_guard.domain.services.monitor_data import MonitorDataService
from exam_guard.schemas.monitor_data import CreateMonitorDataDTO, MonitorDataInDTO


@pytest.mark.asyncio
class TestMonitorDataService:
    async def test_add_monitor_data(self) -> None:
        repo = AsyncMock()
        service = MonitorDataService(repo)
        pyload = {'eui': str(uuid_lib.uuid4()), 'ts': int(time.time()), 'pulse': 60}
        in_dto = MonitorDataInDTO(**pyload)

        await service.add_monitor_data(in_dto)
        monitor_data = CreateMonitorDataDTO(monitor_id=in_dto.eui, data=in_dto.model_dump(), ts=in_dto.ts)
        repo.create.assert_called_with(monitor_data)
