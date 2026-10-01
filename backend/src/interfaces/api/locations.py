from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.locations.assignment_service import (
    DeviceZoneAssignmentService,
)
from src.application.locations.config_service import LocationConfigService
from src.application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    LocationDto,
    ZoneConfigDto,
    ZoneCreateDto,
    ZoneUpdateDto,
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


def get_assignment_service(
    db: Session = Depends(get_db),
) -> DeviceZoneAssignmentService:
    return DeviceZoneAssignmentService(LocationRepository(db))


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
        ) from error


@router.get(
    "",
    response_model=list[LocationDto],
)
def list_locations(
    service: LocationConfigService = Depends(get_location_service),
):
    locations = service.list_locations()

    return [
        LocationDto(
            id=location.id,
            name=location.name,
        )
        for location in locations
    ]


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


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
):
    deleted = service.delete_location(location_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )


@router.post(
    "/{location_id}/zones",
    response_model=ZoneConfigDto,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneCreateDto,
    service: LocationConfigService = Depends(get_location_service),
):
    try:
        zone = service.add_zone(
            location_id=location_id,
            name=request.name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    return ZoneConfigDto(
        id=zone.id,
        location_id=zone.location_id,
        name=zone.name,
        moisture_threshold_low=float(zone.moisture_threshold_low),
        moisture_threshold_high=float(zone.moisture_threshold_high),
        schedule=zone.schedule,
    )


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneConfigDto,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneUpdateDto,
    service: LocationConfigService = Depends(get_location_service),
):
    try:
        zone = service.update_zone(
            location_id=location_id,
            zone_id=zone_id,
            name=request.name,
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone or location not found.",
        )

    return ZoneConfigDto(
        id=zone.id,
        location_id=zone.location_id,
        name=zone.name,
        moisture_threshold_low=float(zone.moisture_threshold_low),
        moisture_threshold_high=float(zone.moisture_threshold_high),
        schedule=zone.schedule,
    )


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
):
    result = service.delete_zone(
        location_id,
        zone_id,
    )

    if result == "missing":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone or location not found.",
        )

    if result == "last":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last zone.",
        )


@router.get(
    "/{location_id}/zones",
    response_model=list[ZoneConfigDto],
)
def list_zones(
    location_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
):
    zones = service.list_zones(location_id)

    if zones is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    return [
        ZoneConfigDto(
            id=zone.id,
            location_id=zone.location_id,
            name=zone.name,
            moisture_threshold_low=float(zone.moisture_threshold_low),
            moisture_threshold_high=float(zone.moisture_threshold_high),
            schedule=zone.schedule,
        )
        for zone in zones
    ]


@router.get(
    "/{location_id}/zones/{zone_id}/devices",
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    service: DeviceZoneAssignmentService = Depends(
        get_assignment_service
    ),
):
    devices = service.list_zone_devices(
        location_id=location_id,
        zone_id=zone_id,
    )

    if devices is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone or location not found.",
        )

    return devices