"""change id to string in payments

Revision ID: a48af74afbd5
Revises: 3e8af94bada1
Create Date: 2025-06-05 11:36:29.826839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a48af74afbd5'
down_revision: Union[str, None] = '3e8af94bada1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert payments.id from INTEGER to VARCHAR
    with op.batch_alter_table("payments") as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert payments.id back to INTEGER
    with op.batch_alter_table("payments") as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=False
        )
