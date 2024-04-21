import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config import settings


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


async def populate() -> None:
    sqls = [
        """
    INSERT INTO
    monitor_types (uuid, name, monitor_type, sku, frequency)
    VALUES
    (
        '669b8e22-c30b-4999-9098-6f5349f0fd09',
        'Samsung X1-S',
        'heart-rate',
        'X10001',
        60
    ),
    (
        '05ac3e78-f653-4e99-8d25-38a1f2648b37',
        'Polar MX2',
        'heart-rate',
        'MX2001',
        1
    ),
    (
        'b782640c-a305-4b95-a7fa-7d3f9593b2d6',
        'Samsung BPA',
        'blood-pressure',
        'BPA001',
        1
    );
    """,
        """
    INSERT INTO
    monitors (eui, monitor_type_id)
    VALUES
    (
        '6ea67f1e-fc9b-4c36-a808-21259b93f8f9',
        '669b8e22-c30b-4999-9098-6f5349f0fd09'
    ),
    (
        '77c91e84-838e-4699-ab6d-a85e4b9db69f',
        '05ac3e78-f653-4e99-8d25-38a1f2648b37'
    ),
    (
        '539c9710-90d2-407b-89fb-643a6637506a',
        'b782640c-a305-4b95-a7fa-7d3f9593b2d6'
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
        students_register_monitors (student_register_id, monitor_id, value_xpath, interval, threshold, move_end_to)
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
