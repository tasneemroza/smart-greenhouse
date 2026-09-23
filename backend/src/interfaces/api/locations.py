from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.locations.config_service import LocationConfigService
from src.application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
)
from src.domain.locations.errors import ConfigurationError
from src.infrastructure.db import get_db
from src.infrastructure.persistence.location_repository import LocationRepository


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_location_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    return LocationConfigService(LocationRepository(db))


@router.post(
    "/config",
    response_model=LocationConfigDto,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: BuildLocationConfigRequestDto,
    service: LocationConfigService = Depends(get_location_service),
):
    try:
        return service.build_and_save(request)
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigDto,
)
def get_location_config(
    location_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
):
    config = service.get_config(location_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    return config