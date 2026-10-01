"""add sensor readings and sampling

Revision ID: 1331fae3af11
Revises: 9f66efb206af
Create Date: 2026-09-28 05:43:44.477502

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op



revision: str = '1331fae3af11'
down_revision: Union[str, Sequence[str], None] = '9f66efb206af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass