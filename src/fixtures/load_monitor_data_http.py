import asyncio
import logging
import time
from typing import List

import aiohttp
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from fixtures.generate_data import nine_minutes_heart_rate, nine_minutes_heart_rate_x_minute
from fixtures.load_monitor_data import polar_mx_payload, samsung_bpa_payload, samsung_x1s_payload

from config import settings
from utils.dataframe import expand_to_3_hours


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.fixtures')


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


async def truncate(conn: AsyncConnection) -> None:
    sql = 'TRUNCATE TABLE exam_guard.monitor_data;'
    await conn.execute(text(sql))


async def populate_polar_mx_payload(ts_start: int) -> list:
    example = nine_minutes_heart_rate()
    example = [(ts_start + ts, value) for ts, value in example]
    data = expand_to_3_hours(example)
    return [polar_mx_payload(ts, value) for ts, value in data]


async def populate_samsung_bpa_payload(ts_start: int) -> list:
    example = nine_minutes_heart_rate_x_minute()
    example = [(ts_start + ts, value) for ts, value in example]
    data = expand_to_3_hours(example)
    return [samsung_bpa_payload(ts, value) for ts, value in data]


async def populate_samsung_x1s_payload(ts_start: int) -> list:
    example = nine_minutes_heart_rate_x_minute()
    example = [(ts_start + ts, value) for ts, value in example]
    data = expand_to_3_hours(example, unit=60)
    return [samsung_x1s_payload(ts, value) for ts, value in data]


async def send_data_to_endpoint_in_batches(data_payloads: List[dict], batch_size: int = 1000) -> None:
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

    ts_start = int(time.time())
    task0 = populate_samsung_x1s_payload(ts_start)
    task1 = populate_polar_mx_payload(ts_start)
    task2 = populate_samsung_bpa_payload(ts_start)
    data0, data1, data2 = await asyncio.gather(task0, task1, task2)

    await send_data_to_endpoint_in_batches(data0 + data1 + data2)


if __name__ == '__main__':
    asyncio.run(main())
