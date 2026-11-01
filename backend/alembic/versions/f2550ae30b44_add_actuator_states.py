"""add actuator states

Revision ID: f2550ae30b44
Revises: 1a77ab5d14d7
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2550ae30b44"
down_revision: Union[str, Sequence[str], None] = "1a77ab5d14d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "actuator_states",
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=32),
            server_default=sa.text("'idle'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("device_id"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO actuator_states (device_id, state)
            SELECT id, 'idle'
            FROM devices
            WHERE role = 'actuator'
            ON CONFLICT (device_id) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_table("actuator_states")
