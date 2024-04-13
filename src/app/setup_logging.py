import logging.config
import os

import yaml

from config import settings


APP_ENV = os.getenv('APP_ENV', 'dev')


def setup_logging() -> None:
    env = settings.APP_ENV
    if env == 'test':
        env = 'dev'
    path = f'logging.{env}.yaml'
    with open(path, 'rt', encoding='utf-8') as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
