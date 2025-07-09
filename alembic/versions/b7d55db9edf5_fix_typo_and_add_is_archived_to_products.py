"""Fix typo and add is_archived to products

Revision ID: b7d55db9edf5
Revises: 074ec231e912
Create Date: 2025-07-07 09:56:35.799581
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'b7d55db9edf5'
down_revision: Union[str, None] = '074ec231e912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("products")]

    if "is_archived" not in columns:
        op.add_column(
            'products',
            sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false'), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("products")]
    if "is_archived" in columns:
        op.drop_column('products', 'is_archived')
