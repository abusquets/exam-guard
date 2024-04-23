import argparse
import asyncio
import sys
import uuid as uuid_lib

from app.app_container import AppContainer
from app.worker import Worker
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository, MonitorDataFilter


SAMSUNG_X1S = '6ea67f1e-fc9b-4c36-a808-21259b93f8f9'  # minute
POLAR_MX = '77c91e84-838e-4699-ab6d-a85e4b9db69f'
SAMSUNG_BPA = '539c9710-90d2-407b-89fb-643a6637506a'

di = AppContainer()
repo: AbstractMonitorDataRepository = di.monitor_data_repository


async def main(slice: int) -> None:
    if first := await repo.first(MonitorDataFilter(monitor_id=uuid_lib.UUID(POLAR_MX))):
        ts = first.ts + (slice * 30)
        await Worker()._check_current_students(ts)  # noqa


parser = argparse.ArgumentParser('Fake Monitor')
parser.add_argument('slice', help='Allowed values [1-18]', type=int)
args = parser.parse_args()
slice = int(args.slice)
if slice < 1 or slice > 18:
    sys.exit('Allowed values [1-18]')

asyncio.run(main(slice))
