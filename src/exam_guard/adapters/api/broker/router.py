import logging

from fastapi import FastAPI
from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue
from faststream.rabbit.fastapi import (
    Logger,
    RabbitMessage,
    RabbitRouter,
)

from app.app_container import AppContainer
from config import settings
from exam_guard.domain.ports.repositories.monitor_data import AbstractMonitorDataRepository
from exam_guard.domain.services.monitor_data import MonitorDataService
from exam_guard.schemas.monitor_data import MonitorDataInDTO


router = RabbitRouter(settings.BROKER_URL, schema_url='/asyncapi', include_in_schema=False, log_level=logging.DEBUG)
broker = router.broker


task_exchange = RabbitExchange(
    name='task-exchange',
    type=ExchangeType.DIRECT,
    durable=True,
)
task_queue = RabbitQueue(
    name='task-queue',
    durable=True,
    arguments={'x-dead-letter-exchange': 'dlx-exchange', 'x-dead-letter-routing-key': 'dlx-key'},
)
dlx_exchange = RabbitExchange(name='dlx-exchange', durable=True)
dlx_queue = RabbitQueue(
    name='dlx-queue',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'task-exchange',
        'x-dead-letter-routing-key': 'task-key',
        'x-message-ttl': settings.BROKER_RETRY_DELAY_IN_SECONDS * 1000,
    },
)

errors_exchange = RabbitExchange('errors-exchange', type=ExchangeType.DIRECT, durable=True)
errors_queue = RabbitQueue('errors-queue', durable=True)

publisher_task = broker.publisher(queue=task_queue, exchange=task_exchange, persist=True)
publisher_errors = broker.publisher(queue=errors_queue, exchange=errors_exchange, persist=True)


@router.after_startup
async def declare(_: FastAPI) -> None:
    _task_exchange = await broker.declare_exchange(task_exchange)
    _dlx_exchange = await broker.declare_exchange(dlx_exchange)
    _task_queue = await broker.declare_queue(task_queue)
    _dlx_queue = await broker.declare_queue(dlx_queue)
    await _task_queue.bind(_task_exchange, routing_key='task-key')
    await _dlx_queue.bind(_dlx_exchange, routing_key='dlx-key')

    _errors_exchange = await broker.declare_exchange(errors_exchange)
    _errors_queue = await broker.declare_queue(errors_queue)
    await _errors_queue.bind(_errors_exchange, routing_key='errors-key')


# TODO: temporary solution, waiting for help
# https://github.com/airtai/faststream/discussions/1387
def get_monitor_data_repository() -> AbstractMonitorDataRepository:
    return AppContainer().monitor_data_repository


# Is not possible to register the function manually due this error:
# TypeError: subscribe() missing 1 required positional argument: 'handler'
# pydantic.errors.PydanticUndefinedAnnotation: name 'AnyDict' is not defined
# monitor_data_repository: Any, Is not possible use monitor_data_repository: MonitorDataRepository
@router.subscriber(task_queue, task_exchange, retry=False, no_ack=True)
async def handle_event(
    input: MonitorDataInDTO,
    msg: RabbitMessage,
    # monitor_data_repository: Annotated[
    #     AbstractMonitorDataRepository, Depends(
    #         lambda: AppContainer().monitor_data_repository
    #     )
    # ],
    logger: Logger,
) -> None:
    try:
        service = MonitorDataService(
            get_monitor_data_repository(),
        )
        await service.add_monitor_data(input)
    except Exception:
        logger.error('Error handling the message', exc_info=True)
        if (
            'x-death' in msg.headers
            and msg.headers.get('x-death', [])[0].get('count', 0) == settings.BROKER_RETRY_TIMES
        ):
            logger.info(f'The message has been moved to errors exchange after {settings.BROKER_RETRY_TIMES} retries')
            await publisher_errors.publish(input.model_dump(), routing_key='errors-key')
            await msg.ack()
        else:
            await msg.reject(requeue=False)

    else:
        logger.info('The message has been processed successfully')
        await msg.ack()
