import logging

from faststream.rabbit import RabbitBroker

from config import settings
from exam_guard.adapters.api.handlers.stream_data import BROKER_REGISTRY as EXAM_GUARD_BROKER_REGISTRY


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.broker')

broker = RabbitBroker(settings.BROKER_URL)


for registry in EXAM_GUARD_BROKER_REGISTRY:
    exchange = registry.pop('exchange')
    queue = registry.pop('queue')
    handler = registry.pop('handler')
    broker.subscriber(exchange, queue, **registry)(handler)
