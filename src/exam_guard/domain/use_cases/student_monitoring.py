import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple

from config import settings
from exam_guard.domain.entities.student_register import StudentRegisterEntity
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository
from exam_guard.domain.use_cases.monitor_alert import MonitorAlertUseCase
from utils.parse_eval import VariablesType, eval_expr


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.StudentMonitoringUseCase')


class StudentMonitoringUseCase:
    def __init__(self, monitor_data_repository: AbstractMonitorDataRepository, sample_rate: int):
        self._monitor_data_repository = monitor_data_repository
        self._sample_rate = sample_rate
        self._student_register: Optional[StudentRegisterEntity] = None
        self._registered_monitors: Dict[int, MonitorAlertUseCase] = {}

    def setup(self, student_register: StudentRegisterEntity) -> None:
        if self._student_register:
            raise ValueError(f'Error: Monitoring for `{student_register.student}` already set up.')
        self._student_register = student_register

    @property
    def student_register(self) -> StudentRegisterEntity:
        if not self._student_register:
            raise ValueError('Monitor not ready, call setup' 'to attach the student.')
        return self._student_register

    def inform_suspicious(self) -> None:
        logger.warning(f'Suspicious data for student {self.student_register.student}')

    async def execute(self, current_ts: Optional[int] = None) -> None:
        """
        This method will be responsible for checking the student's data.
        To minimize the working tasks we start by checking data from
        heart rate, then we move to blood pressure.
        - heart rate check
            - get the first value of the serie
            - get the last 1.5 minutes of the serie
            - calculate the increase of all values
                - if all the values are over 30% check the preasure
        - blood pressure
        """
        start_time = time.time()

        if not self._student_register:
            logger.error('Student register is not set up')
            raise ValueError('Student register is not set up')

        logger.debug(f'Checking the student: {self.student_register.student}...')
        new_monitors: List[int] = []
        for monitor in self._student_register.monitors:
            new_monitors.append(monitor.id)
            if monitor.id not in self._registered_monitors:
                monitor_alert = MonitorAlertUseCase(self._monitor_data_repository, self._sample_rate)
                monitor_alert.setup(monitor)
                self._registered_monitors[monitor.id] = monitor_alert

        registered_monitors: List[int] = list(self._registered_monitors.keys())
        for registered_monitor_id in registered_monitors:
            if registered_monitor_id not in new_monitors:
                # Explicit destroy
                if obj := self._registered_monitors.pop(registered_monitor_id, None):
                    logger.debug('Destroying monitor...')
                    del obj

        tasks = [monitor.execute(current_ts) for monitor in self._registered_monitors.values()]
        results: Optional[List[Optional[List[Tuple[int, float]]]]] = await asyncio.gather(*tasks)
        logger.debug(
            f'Checking the student: {self.student_register.student}... Done',
            extra={
                'monitors': len(registered_monitors),
                'execute_results': results,
                'tasks': len(tasks),
            },
        )

        # Check if all the results are a list of values
        # We should rules in the future compare the results between
        # the monitors
        if results and all(results):
            checks = []
            variables: VariablesType = {}
            for i in range(len(results)):
                row = results[i]
                if not row:
                    continue
                start = row[0]
                end = row[-1]
                variables[f'ts_start_{i}'] = start[0]
                variables[f'ts_end_{i}'] = end[0]
                variables[f'value_start_{i}'] = start[1]
                variables[f'value_end_{i}'] = end[1]

            for rule in self._student_register.rules:
                res = False
                try:
                    res = eval_expr(rule, variables)
                except Exception as e:
                    logger.error(f'Error evaluating rule: {rule}', exc_info=e)
                checks.append(res)

            if checks and all(checks):
                self.inform_suspicious()

        elapsed_time = time.time() - start_time
        logger.info(f'Finished checking the student: {self.student_register.student}' f' in {elapsed_time:.2f} seconds')
