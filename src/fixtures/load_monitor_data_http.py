import asyncio
import logging
from typing import List

import aiohttp
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


async def truncate(conn: AsyncConnection) -> None:
    sql = 'TRUNCATE TABLE exam_guard.monitor_data;'
    await conn.execute(text(sql))


async def populate_blood_pressure() -> list:
    example = nine_minutes_blood_pressure()
    data = expand_to_3_hours(example)
    return [blood_pressure_monitor_payload(ts, value) for ts, value in data]


async def populate_heart_rate() -> list:
    example = nine_minutes_heart_rate()
    data = expand_to_3_hours(example)
    return [heart_rate_monitor_payload(ts, value) for ts, value in data]


async def send_data_to_endpoint_in_batches(data_payloads: List[dict], batch_size: int = 500) -> None:
    endpoint = 'http://127.0.0.1:80/exam-guard/monitor-data/stream'
    headers = {'Authorization': 'Bearer faketoken'}

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(data_payloads), batch_size):
            batch = data_payloads[i : i + batch_size]
            tasks = [session.post(endpoint, json=payload, headers=headers) for payload in batch]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in responses:
                if isinstance(response, aiohttp.ClientResponse):
                    if response.status != 204:
                        logger.error(f'Failed to send data: {await response.text()}')
                else:
                    logger.error(f'Failed to send data: {response}')


async def main() -> None:
    async with engine.begin() as conn:
        await truncate(conn)
    task1 = populate_heart_rate()
    task2 = populate_blood_pressure()
    data1, data2 = await asyncio.gather(task1, task2)

    await send_data_to_endpoint_in_batches(data1 + data2)


if __name__ == '__main__':
    asyncio.run(main())
