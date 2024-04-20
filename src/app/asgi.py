from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response

from app.app_container import AppContainer
from app.setup_logging import setup_logging
from config import settings
from exam_guard.adapters.api.broker.router import (
    publisher_task,
    router as broker_router,
)
from exam_guard.adapters.api.http.router import router as exam_guard_router
from shared.exceptions import APPExceptionError


setup_logging()

logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.asgi')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    di = AppContainer()
    app.state.di = di
    app.state.publisher_task = publisher_task
    start_rabbit = os.environ.get('START_RABBIT', False)
    logger.info(f'START_RABBIT: {start_rabbit}')
    if start_rabbit:
        async with broker_router.lifespan_context(app):
            yield
    else:
        yield


app = FastAPI(debug=settings.DEBUG, lifespan=lifespan)


@app.get('/')
async def root() -> dict:
    return {'message': 'Hello World'}


app.include_router(exam_guard_router)
app.include_router(broker_router)


@app.exception_handler(APPExceptionError)
async def custom_exception_handler(_: Request, exc: APPExceptionError) -> Response:
    return Response(
        status_code=exc.status_code,
        content={'error': {'code': exc.code, 'message': exc.message}},
    )
