from typing import Any, AsyncContextManager, AsyncGenerator, Callable, Dict
import uuid as uuid_lib

from faker import Faker
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_container import AppContainer
from exam_guard.domain.ports.repositories.monitor_data import MonitorDataFilter
from exam_guard.infra.database.sqlalchemy.models import monitor_data, monitors


fake = Faker()

AsyncSessionCtxT = Callable[[], AsyncContextManager[AsyncSession]]


@pytest_asyncio.fixture(scope='function')
async def monitors_example(async_session_maker: AsyncSessionCtxT) -> AsyncGenerator[dict, None]:
    eui = uuid_lib.uuid4()
    data = {'eui': eui, 'name': fake.name(), 'monitor_type': 'heart-rate', 'interval': 1}

    async with async_session_maker() as session:
        statement = monitors.insert().values(**data)
        await session.execute(statement)
        await session.commit()
        yield data
        stmt = monitor_data.delete()
        await session.execute(stmt)
        stmt = monitors.delete()
        await session.execute(stmt)


@pytest_asyncio.fixture(scope='function')
async def monitor_data_example(
    async_session_maker: AsyncSessionCtxT, monitors_example: Dict[str, Any]
) -> AsyncGenerator[dict, None]:
    data = {'monitor_id': monitors_example['eui'], 'ts': 1234567, 'data': {'pulse': 60}}

    async with async_session_maker() as session:
        statement = monitor_data.insert().values(**data)
        await session.execute(statement)
        await session.commit()
        yield data
        stmt = monitor_data.delete()
        await session.execute(stmt)


@pytest.mark.asyncio
class TestMonitorDataRepository:
    async def test_first(self, monitor_data_example: Dict[str, Any]) -> None:
        repo = AppContainer().monitor_data_repository
        filter_by = MonitorDataFilter(monitor_id=monitor_data_example['monitor_id'])
        ret = await repo.first(filter_by)
        assert ret is not None
        assert ret.monitor_id == monitor_data_example['monitor_id']
        assert ret.data == monitor_data_example['data']
        assert ret.ts == monitor_data_example['ts']
