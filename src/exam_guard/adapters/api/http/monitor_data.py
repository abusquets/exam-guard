from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from app.app_container import AppContainer
from app.schemas import Session
from app.session_deps import check_access_token
from exam_guard.adapters.api.http.schemas.monitor_data import MonitorDataRequestDTO
from exam_guard.domain.services.monitor_data import MonitorDataService
from exam_guard.schemas.monitor_data import MonitorDataInDTO


router = APIRouter(prefix='/monitor-data')


@router.post(
    '',
    response_class=JSONResponse,
    status_code=204,
    responses={
        204: {'description': 'Item created'},
        422: {'description': 'Unprocessable Entity'},
    },
)
async def add_monitor_data(
    request_data: MonitorDataRequestDTO,
    container: AppContainer = Depends(AppContainer),
    _: Session = Depends(check_access_token),
) -> None:
    in_dto = MonitorDataInDTO.model_validate(request_data.model_dump())
    service = MonitorDataService(
        container.monitor_data_repository,
    )
    await service.add_monitor_data(in_dto)
