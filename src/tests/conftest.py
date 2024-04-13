import asyncio
from asyncio import current_task
from typing import AsyncGenerator, Generator, Iterator

from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.app_container import AppContainer
from app.asgi import app
from config import settings
import exam_guard.infra.database.sqlalchemy.models  # noqa
from infra.database.sqlalchemy.sqlalchemy import metadata


def pytest_addoption(parser: pytest.Parser) -> None:
    # NOTE: when adding or removing an option,
    # remove to remove/add from app/conftest.py:addoption_params
    parser.addoption('--no-db', default=False, action='store_true', help='Disable testing database')


def addoption_params(config: pytest.Config) -> dict[str, bool]:
    return {
        'no-db': config.getoption('--no-db'),
    }


def pytest_configure(config: pytest.Config) -> None:
    params = addoption_params(config)
    if not params.get('no-db'):
        next(_event_loop()).run_until_complete(create_all(_engine()))


def pytest_unconfigure(config: pytest.Config) -> None:
    params = addoption_params(config)
    if not params.get('no-db'):
        next(_event_loop()).run_until_complete(drop_all(_engine()))


def _event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _engine() -> AsyncEngine:
    return create_async_engine(settings.DATABASE_URL, future=True, echo=False)


@pytest.fixture(scope='function', autouse=True)
def engine() -> Generator:
    yield _engine()


@pytest.fixture
def async_session_maker(engine: AsyncEngine) -> Generator:
    yield async_scoped_session(
        async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession), scopefunc=current_task
    )


async def create_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    await engine.dispose()


async def drop_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_root_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://test/api/v1') as ac:
        yield ac


@pytest_asyncio.fixture
async def app_container() -> AsyncGenerator:
    yield AppContainer()


@pytest_asyncio.fixture
async def async_authorized_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        ac.headers.update({'Authorization': 'Bearer woop'})
        yield ac
