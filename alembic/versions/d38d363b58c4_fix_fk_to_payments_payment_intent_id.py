"""Fix FK to payments.payment_intent_id

Revision ID: d38d363b58c4
Revises: 3927472cec49
Create Date: 2025-08-04 10:37:04.289482
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision: str = 'd38d363b58c4'
down_revision: Union[str, None] = '3927472cec49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    # 1. Drop existing foreign key from orders.payment_id → payments.id
    op.drop_constraint('orders_payment_id_fkey', 'orders', type_='foreignkey')

    # 2. Ensure `payment_intent_id` is NOT NULL
    op.alter_column(
        'payments',
        'payment_intent_id',
        existing_type=sa.String(),
        nullable=False
    )

    # 3. Add a UNIQUE constraint on payment_intent_id
    op.create_unique_constraint(
        'uq_payments_payment_intent_id',
        'payments',
        ['payment_intent_id']
    )

    # 4. Drop `id` column and related index/constraints
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_index('ix_payments_id', if_exists=True)
        batch_op.drop_column('id')

    # 5. Create new foreign key orders.payment_id → payments.payment_intent_id
    op.create_foreign_key(
        'orders_payment_id_fkey',
        'orders',
        'payments',
        ['payment_id'],
        ['payment_intent_id']
    )

    # 6. Ensure index on payment_intent_id for fast FK joins
    op.create_index('ix_payments_payment_intent_id', 'payments', ['payment_intent_id'])


def downgrade() -> None:
    """Downgrade schema."""

    # 1. Add back the old ID column
    op.add_column('payments', sa.Column('id', sa.String(), nullable=False))

    # 2. Re-create index on id
    op.create_index('ix_payments_id', 'payments', ['id'])

    # 3. Drop FK to payment_intent_id
    op.drop_constraint('orders_payment_id_fkey', 'orders', type_='foreignkey')

    # 4. Re-create FK to id
    op.create_foreign_key(
        'orders_payment_id_fkey',
        'orders',
        'payments',
        ['payment_id'],
        ['id']
    )

    # 5. Drop unique/index on payment_intent_id
    op.drop_index('ix_payments_payment_intent_id', table_name='payments')
    op.drop_constraint('uq_payments_payment_intent_id', 'payments', type_='unique')

    # 6. Allow nullable again if needed
    op.alter_column(
        'payments',
        'payment_intent_id',
        existing_type=sa.String(),
        nullable=True
    )
