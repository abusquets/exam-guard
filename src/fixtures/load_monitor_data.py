import asyncio
import json
import logging
from typing import Callable, List, Tuple, Union

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from fixtures.generate_data import (
    expand_to_3_hours,
    nine_minutes_blood_pressure,
    nine_minutes_heart_rate,
    nine_minutes_heart_rate_x_minute,
)

from config import settings


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.fixtures')


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


SAMSUNG_X1S = '6ea67f1e-fc9b-4c36-a808-21259b93f8f9'
POLAR_MX = '77c91e84-838e-4699-ab6d-a85e4b9db69f'
SAMSUNG_BPA = '539c9710-90d2-407b-89fb-643a6637506a'


def polar_mx_payload(ts: int, value: float) -> dict:
    return {'eui': SAMSUNG_X1S, 'model': 'X1-S/1.0', 'pulse': value, 'ts': ts}


def samsung_x1s_payload(ts: int, value: float) -> dict:
    return {
        'eui': POLAR_MX,
        'model': 'X1-S',
        'version': '1.1',
        'payload': {'hr': value, 'hrt': 1},
        'ts': ts,
    }


def samsung_bpa_payload(ts: int, value: float) -> dict:
    return {
        'eui': SAMSUNG_BPA,
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


async def populate_polar_mx_payload(conn: AsyncConnection) -> None:
    example = nine_minutes_heart_rate()
    data = expand_to_3_hours(example)
    await sql_insert_monitor_data(conn, POLAR_MX, data, polar_mx_payload)


async def populate_samsung_bpa_payload(conn: AsyncConnection) -> None:
    example = nine_minutes_blood_pressure()
    data = expand_to_3_hours(example)
    await sql_insert_monitor_data(conn, SAMSUNG_BPA, data, samsung_bpa_payload)


async def populate_samsung_x1s_payload(conn: AsyncConnection) -> None:
    example = nine_minutes_heart_rate_x_minute()
    data = expand_to_3_hours(example, unit=60)
    await sql_insert_monitor_data(conn, SAMSUNG_X1S, data, samsung_x1s_payload)


async def main() -> None:
    async with engine.begin() as conn:
        await truncate(conn)
    async with engine.begin() as conn:
        task0 = asyncio.create_task(populate_samsung_x1s_payload(conn))
        task1 = asyncio.create_task(populate_polar_mx_payload(conn))
        task2 = asyncio.create_task(populate_samsung_bpa_payload(conn))
        await asyncio.gather(task0, task1, task2)


if __name__ == '__main__':
    asyncio.run(main())
