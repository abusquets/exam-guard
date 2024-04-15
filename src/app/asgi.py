from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response

from app.broker import broker
from app.setup_logging import setup_logging
from config import settings
from exam_guard.adapters.api.http.router import router as exam_guard_router
from shared.exceptions import APPExceptionError


setup_logging()

logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.asgi')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    await broker.start()
    app.state.broker = broker
    yield
    await broker.close()


app = FastAPI(debug=settings.DEBUG, lifespan=lifespan)


@app.get('/')
async def root() -> dict:
    return {'message': 'Hello World'}


app.include_router(exam_guard_router)


@app.exception_handler(APPExceptionError)
async def custom_exception_handler(_: Request, exc: APPExceptionError) -> Response:
    return Response(
        status_code=exc.status_code,
        content={'error': {'code': exc.code, 'message': exc.message}},
    )
