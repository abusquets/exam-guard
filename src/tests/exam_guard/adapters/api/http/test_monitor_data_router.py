from typing import Any, Dict
from unittest.mock import Mock, patch

from httpx import AsyncClient
import pytest

from exam_guard.schemas.monitor_data import MonitorDataInDTO


@pytest.mark.asyncio
async def test_create_monitor_data_no_credentials(async_root_client: AsyncClient) -> None:
    payload = {
        'eui': '6ea67f1e-fc9b-4c36-a808-21259b93f8f9',
        'version': '1.1',
        'payload': {'hr': 60, 'hrt': 65},
        'ts': 1390980039,
    }
    response = await async_root_client.post('/exam-guard/monitor-data', json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
@patch('exam_guard.domain.services.monitor_data.MonitorDataService.add_monitor_data')
async def test_create_monitor_data(mocked_add_monitor_data: Mock, async_authorized_client: AsyncClient) -> None:
    payload = {
        'eui': '6ea67f1e-fc9b-4c36-a808-21259b93f8f9',
        'version': '1.1',
        'payload': {'hr': 60, 'hrt': 65},
        'ts': 1390980039,
    }
    response = await async_authorized_client.post('/exam-guard/monitor-data', json=payload)
    assert response.status_code == 204
    in_dto = MonitorDataInDTO.model_validate(payload)
    mocked_add_monitor_data.assert_called_with(in_dto)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload',
    [
        {'version': '1.1', 'payload': {'hr': 60, 'hrt': 65}, 'ts': 1390980039},
        {
            'eui': '6ea67f1e-fc9b-4c36-a808-21259b93f8f9',
            'version': '1.1',
            'payload': {'hr': 60, 'hrt': 65},
        },
    ],
)
async def test_create_monitor_data_invalid_payload(
    payload: Dict[str, Any], async_authorized_client: AsyncClient
) -> None:
    response = await async_authorized_client.post('/exam-guard/monitor-data', json=payload)
    assert response.status_code == 422
