from datetime import datetime, timezone

from sqlalchemy import delete, select

from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.sampling_config_dto import SamplingConfigDto
from src.application.sensors.sampling_service import SamplingService
from src.application.sensors.simulation_sampler import SimulationSampler
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.models import DeviceRow, ReadingRow
from src.infrastructure.persistence.reading_repository import ReadingRepository


def get_test_sensor(db):
    return db.scalar(
        select(DeviceRow)
        .where(DeviceRow.role == "sensor")
        .where(DeviceRow.device_type == "moisture_sensor")
        .where(DeviceRow.device_family == "simulation")
        .order_by(DeviceRow.created_at.desc())
    )


def clear_device_readings(db, device_id):
    db.execute(
        delete(ReadingRow).where(
            ReadingRow.device_id == device_id
        )
    )
    db.commit()


def set_simulation_config(device):
    config = dict(device.default_config or {})
    config["protocol"] = "simulation"
    config["unit"] = "vwc"
    device.default_config = config


def test_reading_ingest_stores_simulation_reading():
    db = SessionLocal()

    try:
        device = get_test_sensor(db)

        assert device is not None

        clear_device_readings(db, device.id)

        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)

        db.commit()

        repository = ReadingRepository(db)
        ingest = ReadingIngest(db, repository)

        timestamp = datetime(
            2026,
            9,
            29,
            12,
            0,
            tzinfo=timezone.utc,
        )

        reading = ingest.read(
            device.id,
            now=timestamp,
        )

        assert reading.device_id == device.id
        assert 30.0 <= reading.value <= 70.0
        assert reading.unit == "vwc"
        assert reading.source == "simulation"
        assert reading.recorded_at == timestamp

        saved = db.scalar(
            select(ReadingRow)
            .where(ReadingRow.device_id == device.id)
            .where(ReadingRow.recorded_at == timestamp)
        )

        assert saved is not None
        assert float(saved.value) == reading.value
        assert saved.unit == "vwc"
        assert saved.source == "simulation"

    finally:
        clear_device_readings(db, device.id)
        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)
        db.commit()
        db.close()


def test_simulation_sampler_respects_interval():
    db = SessionLocal()

    try:
        device = get_test_sensor(db)

        assert device is not None

        clear_device_readings(db, device.id)

        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)

        db.commit()

        repository = ReadingRepository(db)
        ingest = ReadingIngest(db, repository)
        sampler = SimulationSampler(db, ingest)

        first_time = datetime(
            2026,
            9,
            29,
            13,
            0,
            tzinfo=timezone.utc,
        )

        first_result = sampler.run_once(first_time)

        assert first_result.sampled >= 1

        first_reading = repository.latest_for_device(
            device.id
        )

        assert first_reading is not None
        assert first_reading.recorded_at == first_time

        second_time = datetime(
            2026,
            9,
            29,
            13,
            0,
            30,
            tzinfo=timezone.utc,
        )

        second_result = sampler.run_once(second_time)

        assert second_result.sampled == 0

        second_reading = repository.latest_for_device(
            device.id
        )

        assert second_reading is not None
        assert second_reading.recorded_at == first_time

    finally:
        clear_device_readings(db, device.id)
        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)
        db.commit()
        db.close()


def test_simulation_sampler_respects_tracking_disabled():
    db = SessionLocal()

    try:
        device = get_test_sensor(db)

        assert device is not None

        clear_device_readings(db, device.id)

        device.tracking_enabled = False
        device.sampling_interval_seconds = 60
        set_simulation_config(device)

        db.commit()

        repository = ReadingRepository(db)
        ingest = ReadingIngest(db, repository)
        sampler = SimulationSampler(db, ingest)

        timestamp = datetime(
            2026,
            9,
            29,
            14,
            0,
            tzinfo=timezone.utc,
        )

        before = repository.latest_for_device(device.id)

        result = sampler.run_once(timestamp)

        after = repository.latest_for_device(device.id)

        assert result.checked >= 0

        if before is None:
            assert after is None
        else:
            assert after is not None
            assert after.recorded_at == before.recorded_at

    finally:
        clear_device_readings(db, device.id)
        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)
        db.commit()
        db.close()


def test_simulation_sampler_skips_mqtt_device():
    db = SessionLocal()

    try:
        device = get_test_sensor(db)

        assert device is not None

        clear_device_readings(db, device.id)

        device.tracking_enabled = True
        device.sampling_interval_seconds = 60

        config = dict(device.default_config or {})
        config["protocol"] = "mqtt"
        config["unit"] = "vwc"
        device.default_config = config

        db.commit()

        repository = ReadingRepository(db)
        ingest = ReadingIngest(db, repository)
        sampler = SimulationSampler(db, ingest)

        timestamp = datetime(
            2026,
            9,
            29,
            15,
            0,
            tzinfo=timezone.utc,
        )

        before = repository.latest_for_device(device.id)

        result = sampler.run_once(timestamp)

        after = repository.latest_for_device(device.id)

        assert result.skipped >= 1

        if before is None:
            assert after is None
        else:
            assert after is not None
            assert after.recorded_at == before.recorded_at

    finally:
        clear_device_readings(db, device.id)
        device.tracking_enabled = True
        device.sampling_interval_seconds = 60
        set_simulation_config(device)
        db.commit()
        db.close()


def test_sampling_service_updates_configuration():
    db = SessionLocal()

    try:
        device = get_test_sensor(db)

        assert device is not None

        service = SamplingService(db)

        config = SamplingConfigDto(
            sampling_interval_seconds=45,
            tracking_enabled=False,
        )

        updated = service.update(
            device.id,
            config,
        )

        assert updated.sampling_interval_seconds == 45
        assert updated.tracking_enabled is False

        db.refresh(device)

        assert device.sampling_interval_seconds == 45
        assert device.tracking_enabled is False

    finally:
        device.sampling_interval_seconds = 60
        device.tracking_enabled = True
        set_simulation_config(device)
        db.commit()
        db.close()

