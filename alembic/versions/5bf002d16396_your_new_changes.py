"""Your new changes

Revision ID: 5bf002d16396
Revises: 61a5cc1962be
Create Date: 2025-06-05 10:52:03.871995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5bf002d16396'
down_revision: Union[str, None] = '61a5cc1962be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    # Check if 'user_product_unique' constraint exists
    result = conn.execute(
        sa.text("SELECT 1 FROM pg_constraint WHERE conname = 'user_product_unique';")
    ).fetchone()

    # Drop tables and indexes
    op.drop_index(op.f('ix_addresses_id'), table_name='addresses')
    op.drop_table('addresses')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_table('payments')

    # Create unique constraint only if it does not exist
    if not result:
        op.create_unique_constraint('user_product_unique', 'favorites', ['user_uid', 'product_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('user_product_unique', 'favorites', type_='unique')
    op.create_table('payments',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('order_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column('currency', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('payment_method', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.uid'], name=op.f('payments_user_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('payments_pkey'))
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=True)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_table('addresses',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_uid', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], name=op.f('addresses_user_uid_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('addresses_pkey')),
        sa.UniqueConstraint('user_uid', name=op.f('uc_user_address'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_addresses_id'), 'addresses', ['id'], unique=False)
