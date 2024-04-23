import asyncio
import logging
import time
from typing import Dict, List, Optional

from app.app_container import AppContainer
from app.setup_logging import setup_logging
from exam_guard.domain.entities.student_register import StudentRegisterEntity
from exam_guard.domain.services.student_register import StudentRegisterService
from exam_guard.domain.use_cases.student_monitoring import StudentMonitoringUseCase


setup_logging()

logger = logging.getLogger('exam_guard.Worker')


class Worker:
    SAMPLE_RATE = 30  # seconds

    def __init__(self) -> None:
        self.iterations = 0
        logger.debug(f'Worker initialized with sample_rate `{self.SAMPLE_RATE}` seconds.')
        self._current_students_register: Dict[str, StudentMonitoringUseCase] = {}
        self.app_container = AppContainer()
        self._student_register_service = StudentRegisterService(
            student_register_repository=self.app_container.student_register_repository
        )

    def _enable_monitoring(self, student_register: StudentRegisterEntity) -> None:
        monitor = StudentMonitoringUseCase(self.app_container.monitor_data_repository, self.SAMPLE_RATE)
        self._current_students_register[student_register.uuid] = monitor
        monitor.setup(student_register)

    def _disable_monitor(self, student_register_id: int) -> None:
        """woops, I forgot to implement this method!"""

    async def _check_current_students(self, current_ts: Optional[int] = None) -> None:
        students_register = await self._student_register_service.curentlly_active_students()
        logger.info(f'Currently active students `{len(students_register)}`')
        checked: List[str] = []
        for student_register in students_register:
            checked.append(student_register.uuid)
            if student_register.uuid not in self._current_students_register:
                self._enable_monitoring(student_register)
        to_execute = [monitor.execute(current_ts) for monitor in self._current_students_register.values()]
        await asyncio.gather(*to_execute)

    async def run_main(self) -> None:
        while True:
            start_time = time.time()
            self.iterations += 1
            logger.debug(f'Worker iterations: {self.iterations}')
            await self._check_current_students(int(start_time))
            elapsed_time = time.time() - start_time
            logger.debug(f'Elapsed time: {elapsed_time}')
            await asyncio.sleep(self.SAMPLE_RATE - elapsed_time)


if __name__ == '__main__':
    logger.debug('Starting the worker...')
    worker = Worker()
    asyncio.run(worker.run_main())
