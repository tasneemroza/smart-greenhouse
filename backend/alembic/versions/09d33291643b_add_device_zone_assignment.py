"""add device zone assignment"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "09d33291643b"
down_revision: Union[str, Sequence[str], None] = "eddfb52b8e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "zone_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_devices_zone_id",
        "devices",
        ["zone_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_devices_zone_id",
        "devices",
        "zones",
        ["zone_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_devices_zone_id",
        "devices",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_devices_zone_id",
        table_name="devices",
    )

    op.drop_column(
        "devices",
        "zone_id",
    )