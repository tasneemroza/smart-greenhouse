from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.devices.dto import DeviceDto
from src.application.devices.family_service import DeviceFamilyService
from src.application.devices.mappers import devices_to_dtos
from src.infrastructure.db import get_db
from src.infrastructure.persistence.device_repository import DeviceRepository


router = APIRouter(prefix="/api/devices", tags=["devices"])


def get_device_service(
    db: Session = Depends(get_db),
) -> DeviceFamilyService:
    return DeviceFamilyService(DeviceRepository(db))


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
        )