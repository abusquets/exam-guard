import datetime
import logging
import time
from typing import List, Optional, Tuple
import uuid as uuid_lib

import dpath

from config import settings
from exam_guard.domain.entities.monitor_data import MonitorDataEntity
from exam_guard.domain.entities.student_register import MonitorRegisterEntity
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository, MonitorDataFilter
from utils.dataframe import extract_outliers


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.MonitorAlertUseCase')


class MonitorAlertUseCase:
    def __init__(self, monitor_data_repository: AbstractMonitorDataRepository, sample_rate: int):
        self._monitor_data_repository = monitor_data_repository
        self._sample_rate = sample_rate
        self._monitor: Optional[MonitorRegisterEntity] = None
        self._first_value: Optional[MonitorDataEntity] = None

    def setup(self, monitor: MonitorRegisterEntity) -> None:
        if self._monitor:
            logger.warning(f'Error: Monitor `{monitor.monitor.monitor_type.name}` already set up.')
            raise ValueError('Error: Monitor already set up.')
        self._monitor = monitor

    @property
    def monitor(self) -> MonitorRegisterEntity:
        if not self._monitor:
            logger.warning('Monitor not ready, call setup' 'to attach it.')
            raise ValueError('Monitor not ready, call setup' 'to attach it.')
        return self._monitor

    async def get_first_value(self) -> Optional[MonitorDataEntity]:
        if not self._first_value:
            self._first_value = await self._monitor_data_repository.first(
                MonitorDataFilter(monitor_id=self.monitor.monitor.eui)
            )
        if not self._first_value:
            logger.warning(f'No data found for monitor `{self.monitor.monitor.monitor_type.name}`')
        return self._first_value

    async def get_monitor_data(self, monitor_id: uuid_lib.UUID, ts_start: int, ts_end: int) -> List[MonitorDataEntity]:
        return await self._monitor_data_repository.list_filter(
            MonitorDataFilter(
                monitor_id=monitor_id,
                ts_between=(ts_start, ts_end),
            )
        )

    async def _execute(self, current_ts: Optional[int] = None) -> Optional[List[Tuple[int, float]]]:
        logger.info('Checking the MonitorAlertUseCase')

        first_item = await self.get_first_value()
        if not first_item:
            logger.warning('No first value found')
            return None

        logger.debug(f'First data value `data`: {first_item.data}')
        if current_ts is None:
            current_ts = int(time.time())
        ts_end = current_ts - self.monitor.move_end_to
        to_rest = (
            self.monitor.monitor.monitor_type.frequency
            if self.monitor.monitor.monitor_type.frequency > self._sample_rate
            else self._sample_rate
        )
        ts_start = ts_end - self.monitor.interval - to_rest

        logger.debug(f'DIFF {ts_end - ts_start}')
        logger.debug(f'FROM {datetime.datetime.fromtimestamp(ts_start)}')
        logger.debug(f'TO {datetime.datetime.fromtimestamp(ts_end)}')

        monitor_data = await self.get_monitor_data(self.monitor.monitor.eui, ts_start, ts_end)
        logger.debug(
            f'Found {len(monitor_data)} items to check',
            extra={
                'monitor': self.monitor.monitor.eui.hex,
                'ts_start': ts_start,
                'ts_end': ts_end,
                'value_xpath': self.monitor.value_xpath,
                'example': monitor_data[0] if monitor_data else None,
            },
        )

        data = [(item.ts, dpath.get(item.data, self.monitor.value_xpath)) for item in monitor_data]
        _first_value = dpath.get(first_item.data, self.monitor.value_xpath)
        if not _first_value:
            logger.warning('No first value found')
            return None
        if isinstance(_first_value, str):
            try:
                first_value = float(_first_value)
            except ValueError:
                logger.warning('First value is not a number')
                return None
        else:
            first_value = _first_value

        suspicious_data = extract_outliers(first_value, data, self.monitor.threshold, self.monitor.interval_to_check)
        if suspicious_data:
            # TODO: More info for logging
            logger.warning(f'Suspicious {self.monitor.id} checking {self.monitor.monitor.monitor_type}')
        return suspicious_data

    async def execute(self, current_ts: Optional[int] = None) -> Optional[List[Tuple[int, float]]]:
        try:
            return await self._execute(current_ts)
        except Exception as e:
            logger.error(f'Error on MonitorAlertUseCase: {e}', exc_info=True)
            return None
