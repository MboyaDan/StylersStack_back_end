"""Mark drop default on payments.id as applied

Revision ID: 2bf1f2c9fffa
Revises: a48af74afbd5
Create Date: 2025-06-05 11:54:54.144090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bf1f2c9fffa'
down_revision: Union[str, None] = 'a48af74afbd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
