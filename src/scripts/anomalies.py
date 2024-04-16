import asyncio
import logging

import pandas as pd
from sqlalchemy import Result, text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from config import settings


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.fixtures')


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)


SAMSUNG_X1S = '6ea67f1e-fc9b-4c36-a808-21259b93f8f9'
POLAR_MX = '77c91e84-838e-4699-ab6d-a85e4b9db69f'
SAMSUNG_BPA = '539c9710-90d2-407b-89fb-643a6637506a'


def cursor_to_df(cursor: Result) -> pd.DataFrame:
    df = pd.DataFrame([])
    values = cursor.fetchall()
    if values:
        df = pd.DataFrame(values)
        df.columns = cursor.keys()
    return df


async def get_data(conn: AsyncConnection, eui: str) -> pd.DataFrame:
    sql = """
        SELECT ts, (data->>'pulse')::float as value FROM exam_guard.monitor_data WHERE monitor_id = :eui;
    """
    cursor = await conn.execute(text(sql), {'eui': eui})
    return cursor_to_df(cursor)


async def main() -> None:
    async with engine.begin() as conn:
        df = await get_data(conn, POLAR_MX)
        df['is_anomaly'] = 0
        threshold = 30
        start_value = df['value'][0]
        value_threshold = start_value + (start_value * threshold / 100)
        df.loc[df['value'] > value_threshold, 'is_anomaly'] = 1
        # print(df)


if __name__ == '__main__':
    asyncio.run(main())
