from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import devices_to_dtos
from src.application.locations.assignment_service import (
    DeviceZoneAssignmentService,
)
from src.application.locations.dto import DeviceZoneAssignmentDto
from src.application.sensors.sampling_config_dto import SamplingConfigDto
from src.application.sensors.sampling_service import SamplingService
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.location_repository import LocationRepository


router = APIRouter(prefix="/api/devices", tags=["devices"])


def get_device_service(
    db: Session = Depends(get_db),
) -> DeviceFamilyService:
    return DeviceFamilyService(DeviceRepository(db))


def get_sampling_service(
    db: Session = Depends(get_db),
) -> SamplingService:
    return SamplingService(db)


def get_assignment_service(
    db: Session = Depends(get_db),
) -> DeviceZoneAssignmentService:
    return DeviceZoneAssignmentService(LocationRepository(db))


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    service: DeviceFamilyService = Depends(get_device_service),
):
    devices = service.list_devices(
        device_family=family,
        role=role,
    )
    return devices_to_dtos(devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    service: DeviceFamilyService = Depends(get_device_service),
):
    try:
        devices = service.provision_family(family)
        return devices_to_dtos(devices)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch(
    "/{device_id}/sampling",
)
def update_sampling(
    device_id: UUID,
    config: SamplingConfigDto,
    service: SamplingService = Depends(get_sampling_service),
):
    try:
        device = service.update(device_id, config)

        return {
            "device_id": device.id,
            "sampling_interval_seconds": device.sampling_interval_seconds,
            "tracking_enabled": device.tracking_enabled,
        }

    except ValueError as error:
        if str(error) == "Device not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            ) from error

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch(
    "/{device_id}/zone",
    response_model=DeviceDto,
)
def assign_device_to_zone(
    device_id: UUID,
    request: DeviceZoneAssignmentDto,
    service: DeviceZoneAssignmentService = Depends(
        get_assignment_service
    ),
):
    try:
        device = service.assign(
            device_id=device_id,
            zone_id=request.zone_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    return devices_to_dtos([device])[0]