from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.sensors.reading_dto import ReadingDto
from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.service import SensorService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.reading_repository import ReadingRepository


router = APIRouter(prefix="/api/sensors", tags=["sensors"])


class SensorCreateRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    id: UUID
    device_type: str
    display_name: str
    default_config: dict


def get_sensor_service(db: Session = Depends(get_db)) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


def get_reading_ingest(db: Session = Depends(get_db)) -> ReadingIngest:
    repository = ReadingRepository(db)
    return ReadingIngest(db, repository)


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    service: SensorService = Depends(get_sensor_service),
):
    return service.list_sensors()


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    service: SensorService = Depends(get_sensor_service),
):
    try:
        return service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def read_sensor(
    device_id: UUID,
    service: ReadingIngest = Depends(get_reading_ingest),
):
    try:
        return service.read(device_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def list_readings(
    device_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repository = ReadingRepository(db)

    try:
        return repository.list_for_device(
            device_id=device_id,
            limit=limit,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error