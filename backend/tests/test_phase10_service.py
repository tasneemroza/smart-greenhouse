from types import SimpleNamespace
from uuid import uuid4

from src.application.commands.dto import CommandRequest
from src.application.commands.service import CommandService


class FakeStateRepository:
    def __init__(self, device_id, state):
        self.device = SimpleNamespace(
            id=device_id,
            role="actuator",
            device_type="water_pump",
        )
        self.state = SimpleNamespace(
            device_id=device_id,
            state=state,
            updated_at=None,
        )

    def get_actuator(self, device_id):
        return self.device if device_id == self.device.id else None

    def get_state_for_update(self, device_id):
        return self.state if device_id == self.device.id else None


class FakeCommandLogRepository:
    def __init__(self):
        self.records = []

    def create(self, **kwargs):
        record = SimpleNamespace(**kwargs)
        self.records.append(record)
        return record


class FakeDB:
    def __init__(self):
        self.added = []
        self.rollbacks = 0

    def add(self, row):
        self.added.append(row)

    def rollback(self):
        self.rollbacks += 1


def build_service(state):
    device_id = uuid4()
    db = FakeDB()

    service = CommandService.__new__(CommandService)
    service.db = db
    service.state_repository = FakeStateRepository(device_id, state)
    service.log_repository = FakeCommandLogRepository()

    return service, device_id, db


def test_illegal_command_rejected_logged():
    service, device_id, db = build_service("running")

    class NeverExecuteInvoker:
        def run(self, command, port):
            raise AssertionError("Rejected command must not execute")

    service.invoker = NeverExecuteInvoker()

    result = service.execute(
        CommandRequest(
            command_type="start_pump",
            device_id=device_id,
            payload={},
        )
    )

    assert result.status == "rejected"
    assert service.state_repository.state.state == "running"
    assert len(service.log_repository.records) == 1
    assert db.added == []


def test_start_pump_transitions_to_running(monkeypatch):
    service, device_id, db = build_service("idle")

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class FakeInvoker:
        def __init__(self):
            self.executed = False

        def run(self, command, port):
            self.executed = True

    invoker = FakeInvoker()
    service.invoker = invoker

    monkeypatch.setattr(
        "src.application.commands.service.SessionLocal",
        lambda: FakeSession(),
    )
    monkeypatch.setattr(
        "src.application.commands.service.build_actuator_port",
        lambda db: object(),
    )

    result = service.execute(
        CommandRequest(
            command_type="start_pump",
            device_id=device_id,
            payload={},
        )
    )

    assert invoker.executed is True
    assert result.status == "success"
    assert service.state_repository.state.state == "running"
    assert len(service.log_repository.records) == 1
    assert db.added == [service.state_repository.state]
