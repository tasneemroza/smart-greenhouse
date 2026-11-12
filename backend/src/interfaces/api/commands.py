from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.application.commands.dto import CommandRequest, CommandResult
from src.application.commands.service import (
    CommandDeviceNotFoundError,
    CommandService,
    CommandStateNotFoundError,
)
from src.infrastructure.db import get_db


router = APIRouter(prefix="/api/commands", tags=["commands"])


def get_command_service(
    db: Session = Depends(get_db),
) -> CommandService:
    return CommandService(db)


@router.post(
    "",
    response_model=CommandResult,
    responses={
        400: {"description": "Unknown command type"},
        404: {"description": "Actuator not found"},
        409: {
            "model": CommandResult,
            "description": "Command rejected by state guard",
        },
    },
)
def execute_command(
    request: CommandRequest,
    response: Response,
    service: CommandService = Depends(get_command_service),
):
    try:
        result = service.execute(request)

    except CommandDeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    except CommandStateNotFoundError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if result.status == "rejected":
        response.status_code = 409

    return result


@router.get("", response_model=list[CommandResult])
def list_commands(
    limit: int = Query(default=50, ge=1, le=200),
    service: CommandService = Depends(get_command_service),
):
    return service.list_recent(limit)
