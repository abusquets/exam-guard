from typing import Any, AsyncContextManager, AsyncGenerator, Callable, Dict
import uuid as uuid_lib

from faker import Faker
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_container import AppContainer
from exam_guard.domain.ports.repositories.monitor_data import MonitorDataFilter
from exam_guard.infra.database.sqlalchemy.models import monitor_data, monitor_types, monitors


fake = Faker()

AsyncSessionCtxT = Callable[[], AsyncContextManager[AsyncSession]]


@pytest_asyncio.fixture(scope='function')
async def monitor_type_example(async_session_maker: AsyncSessionCtxT) -> AsyncGenerator[dict, None]:
    monitor_type_uuid = uuid_lib.uuid4()
    data = {
        'uuid': monitor_type_uuid,
        'name': fake.name(),
        'monitor_type': 'heart-rate',
        'frequency': 1,
        'sku': '1234567890',
    }

    async with async_session_maker() as session:
        statement = monitor_types.insert().values(**data)
        await session.execute(statement)
        await session.commit()
        yield data
        stmt = monitor_data.delete()
        await session.execute(stmt)
        stmt = monitors.delete()
        await session.execute(stmt)
        stmt = monitor_types.delete()
        await session.execute(stmt)


@pytest_asyncio.fixture(scope='function')
async def monitors_example(
    async_session_maker: AsyncSessionCtxT, monitor_type_example: Dict[str, Any]
) -> AsyncGenerator[dict, None]:
    eui = uuid_lib.uuid4()
    data = {'eui': eui, 'monitor_type_id': monitor_type_example['uuid']}

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
