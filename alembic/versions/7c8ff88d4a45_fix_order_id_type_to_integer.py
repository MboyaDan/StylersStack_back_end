"""Fix order_id type to String and ensure FK relationship

Revision ID: 7c8ff88d4a45
Revises: 29adf5987cd3
Create Date: 2025-07-09 10:53:42.196539
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c8ff88d4a45'
down_revision: Union[str, None] = '29adf5987cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure payments.order_id is String and FK-safe"""
    # First, drop the existing constraint if it exists (optional)
    # Then alter to String (if not already)
    with op.batch_alter_table('payments') as batch_op:
        batch_op.alter_column('order_id',
            existing_type=sa.Integer(),  # Use sa.String() if already String
            type_=sa.String(),
            existing_nullable=True
        )


def downgrade() -> None:
    """Reverse to Integer (NOT recommended if you store 'ORD-XXXX' style IDs)"""
    with op.batch_alter_table('payments') as batch_op:
        batch_op.alter_column('order_id',
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=True,
            postgresql_using='order_id::integer'
        )
