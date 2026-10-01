from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f88c12e79296"
down_revision: Union[str, Sequence[str], None] = "9f66efb206af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "sampling_interval_seconds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("300"),
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "tracking_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE devices
            SET sampling_interval_seconds =
                (default_config->>'sampling_interval_seconds')::numeric::integer
            WHERE jsonb_typeof(default_config->'sampling_interval_seconds') = 'number'
            """
        )
    )

    op.create_table(
        "sensor_readings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Numeric(),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_sensor_readings_device_recorded_at",
        "sensor_readings",
        ["device_id", sa.text("recorded_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sensor_readings_device_recorded_at",
        table_name="sensor_readings",
    )

    op.drop_table("sensor_readings")

    op.drop_column("devices", "tracking_enabled")
    op.drop_column("devices", "sampling_interval_seconds")