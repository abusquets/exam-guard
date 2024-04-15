import asyncio
import json
import logging
from typing import Callable, List, Tuple, Union

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from fixtures.generate_data import expand_to_3_hours, nine_minutes_blood_pressure, nine_minutes_heart_rate

from config import settings


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.fixtures')


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


def heart_rate_monitor_payload(ts: int, value: float) -> dict:
    return {'eui': '77c91e84-838e-4699-ab6d-a85e4b9db69f', 'model': 'X1-S/1.0', 'pulse': value, 'ts': ts}


def blood_pressure_monitor_payload(ts: int, value: float) -> dict:
    return {
        'eui': '539c9710-90d2-407b-89fb-643a6637506a',
        'model': 'BPA',
        'payload': {'bp_sys': value, 'bp_dia': 1},
        'ts': ts,
    }


async def sql_insert_monitor_data(
    conn: AsyncConnection, eui: str, data: List[Tuple[int, Union[int, float]]], payload_func: Callable
) -> None:
    sql = """
        INSERT INTO exam_guard.monitor_data (monitor_id, data, created_at, ts)
        VALUES (:eui, :data, now(), :ts);
    """
    payload_values = []
    for ts, value in data:
        payload = payload_func(ts, value)
        payload_json = json.dumps(payload)
        payload_values.append({'eui': eui, 'data': payload_json, 'ts': ts})

    await conn.execute(text(sql), payload_values)


async def truncate(conn: AsyncConnection) -> None:
    sql = 'TRUNCATE TABLE exam_guard.monitor_data;'
    await conn.execute(text(sql))


async def populate_blood_pressure(conn: AsyncConnection) -> None:
    example = nine_minutes_blood_pressure()
    data = expand_to_3_hours(example)
    await sql_insert_monitor_data(conn, '539c9710-90d2-407b-89fb-643a6637506a', data, blood_pressure_monitor_payload)


async def populate_heart_rate(conn: AsyncConnection) -> None:
    example = nine_minutes_heart_rate()
    data = expand_to_3_hours(example)
    await sql_insert_monitor_data(conn, '77c91e84-838e-4699-ab6d-a85e4b9db69f', data, heart_rate_monitor_payload)


async def main() -> None:
    async with engine.begin() as conn:
        await truncate(conn)
    async with engine.begin() as conn:
        task1 = asyncio.create_task(populate_heart_rate(conn))
        task2 = asyncio.create_task(populate_blood_pressure(conn))
        await asyncio.gather(task1, task2)


if __name__ == '__main__':
    asyncio.run(main())
