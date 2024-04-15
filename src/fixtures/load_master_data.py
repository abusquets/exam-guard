import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config import settings


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


async def populate() -> None:
    sqls = [
        """
    INSERT INTO
    monitors (eui, name, monitor_type, interval)
    VALUES
    (
        '6ea67f1e-fc9b-4c36-a808-21259b93f8f9',
        'Samsung X1-S',
        'heart-rate',
        60
    ),
    (
        '77c91e84-838e-4699-ab6d-a85e4b9db69f',
        'Polar MX2',
        'heart-rate',
        1
    ),
    (
        '539c9710-90d2-407b-89fb-643a6637506a',
        'Samsung BPA',
        'blood-pressure',
        1
    );
    """,
        """
    INSERT INTO
    students_register (uuid, student, active)
    VALUES
    (
        '82f25a6e-87e4-4b67-b111-8648cf5b9479',
        '77914904G',
        true
    );
    """,
        """
    INSERT INTO
        students_register_monitors (student_register_id, monitor_id, value_xpath, interval, threshold, end_subtstract)
    VALUES
    (
        '82f25a6e-87e4-4b67-b111-8648cf5b9479',
        '77c91e84-838e-4699-ab6d-a85e4b9db69f',
        '/pulse',
        90,
        30,
        0
    ),
    (
        '82f25a6e-87e4-4b67-b111-8648cf5b9479',
        '539c9710-90d2-407b-89fb-643a6637506a',
        '/payload/bp_sys',
        120,
        20,
        60
    )
    ;
    """,
    ]

    async with engine.begin() as conn:
        for sql in sqls:
            await conn.execute(text(sql))


async def main() -> None:
    await populate()


if __name__ == '__main__':
    asyncio.run(main())
