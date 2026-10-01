from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.sampling_dto import SamplingResultDto
from src.infrastructure.persistence.models import DeviceRow


class SimulationSampler:
    def __init__(
        self,
        db: Session,
        ingest: ReadingIngest,
    ):
        self.db = db
        self.ingest = ingest

    def run_once(
        self,
        now: datetime | None = None,
    ) -> SamplingResultDto:
        current_time = now or datetime.now(timezone.utc)

        if current_time.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        devices = self.db.scalars(
            select(DeviceRow)
            .where(DeviceRow.role == "sensor")
            .where(DeviceRow.device_family == "simulation")
            .where(DeviceRow.tracking_enabled.is_(True))
        ).all()

        checked = len(devices)
        sampled = 0
        skipped = 0

        for device in devices:
            config = device.default_config or {}
            protocol = config.get("protocol", "simulation")

            if protocol not in {"simulation", "sim"}:
                skipped += 1
                continue

            latest = self.ingest.repository.latest_for_device(device.id)

            if latest is not None:
                elapsed = (
                    current_time - latest.recorded_at
                ).total_seconds()

                if elapsed < device.sampling_interval_seconds:
                    skipped += 1
                    continue

            self.ingest.read(
                device.id,
                now=current_time,
            )

            sampled += 1

        return SamplingResultDto(
            checked=checked,
            sampled=sampled,
            skipped=skipped,
            recorded_at=current_time,
        )