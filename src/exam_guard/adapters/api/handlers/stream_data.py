import logging

from fast_depends import Depends
from faststream.rabbit.annotations import RabbitMessage

from app.app_container import AppContainer
from exam_guard.domain.services.monitor_data import MonitorDataService
from exam_guard.schemas.monitor_data import MonitorDataInDTO


logger = logging.getLogger('{settings.APP_LOGGER_NAME}.handlers')


async def strem_monitor_data(
    body: str, msg: RabbitMessage, container: AppContainer = Depends(lambda: AppContainer())
) -> None:
    logger.info('Message', extra={'content': body})
    in_dto = MonitorDataInDTO.model_validate_json(body)
    service = MonitorDataService(
        container.monitor_data_repository,
    )
    await service.add_monitor_data(in_dto)
    await msg.ack()


BROKER_REGISTRY = [
    {
        'exchange': 'test',
        'queue': 'test',
        'handler': strem_monitor_data,
        'retry': False,
        'description': 'Consumes messages from monitors',
    }
]
