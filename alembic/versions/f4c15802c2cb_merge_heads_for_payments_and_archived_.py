"""merge heads for payments and archived products

Revision ID: f4c15802c2cb
Revises: 64f1ee018e71, b7d55db9edf5
Create Date: 2025-07-09 11:31:12.082602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c15802c2cb'
down_revision: Union[str, None] = ('64f1ee018e71', 'b7d55db9edf5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
