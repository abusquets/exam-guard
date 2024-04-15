from fastapi.routing import APIRouter

from .monitor_data import router as monitor_data_router


router = APIRouter(prefix='/exam-guard', tags=['exam-guard'])
router.include_router(monitor_data_router)
