from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.application.sensors.reading_dto import ReadingDto
from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.sampling_config_dto import SamplingConfigDto
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.reading_repository import ReadingRepository

router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def read_sensor(
    device_id: UUID,
    db: Session = Depends(get_db),
):
    service = ReadingIngest(
        db,
        ReadingRepository(db),
    )

    try:
        return service.read(device_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc