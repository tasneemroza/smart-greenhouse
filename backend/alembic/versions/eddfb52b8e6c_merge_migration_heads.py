"""merge migration heads

Revision ID: eddfb52b8e6c
Revises: 1331fae3af11, f88c12e79296
Create Date: 2026-09-28 05:49:48.145067

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op



revision: str = 'eddfb52b8e6c'
down_revision: Union[str, Sequence[str], None] = ('1331fae3af11', 'f88c12e79296')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass