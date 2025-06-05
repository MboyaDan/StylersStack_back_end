"""Fix Payment FK to users.uid

Revision ID: df8bc54ee77a
Revises: 61ae0dd5b6de
Create Date: 2025-06-04 09:47:09.039715
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'df8bc54ee77a'
down_revision: Union[str, None] = '61ae0dd5b6de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # Safely create unique constraint on carts
    carts_constraints = inspector.get_unique_constraints('carts')
    carts_constraint_names = [c['name'] for c in carts_constraints]
    if 'user_product_unique' not in carts_constraint_names:
        op.create_unique_constraint('user_product_unique', 'carts', ['user_uid', 'product_id'])

    # Safely create unique constraint on favorites
    favorites_constraints = inspector.get_unique_constraints('favorites')
    favorites_constraint_names = [c['name'] for c in favorites_constraints]
    if 'user_product_unique' not in favorites_constraint_names:
        op.create_unique_constraint('user_product_unique', 'favorites', ['user_uid', 'product_id'])

    # Drop indexes and tables as before
    op.drop_index(op.f('ix_addresses_id'), table_name='addresses')
    op.drop_table('addresses')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_table('payments')

    # Alter users table columns
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.drop_column('users', 'name')


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # Safely drop unique constraint on favorites
    favorites_constraints = inspector.get_unique_constraints('favorites')
    favorites_constraint_names = [c['name'] for c in favorites_constraints]
    if 'user_product_unique' in favorites_constraint_names:
        op.drop_constraint('user_product_unique', 'favorites', type_='unique')

    # Safely drop unique constraint on carts
    carts_constraints = inspector.get_unique_constraints('carts')
    carts_constraint_names = [c['name'] for c in carts_constraints]
    if 'user_product_unique' in carts_constraint_names:
        op.drop_constraint('user_product_unique', 'carts', type_='unique')

    # Re-add users.name column and revert users.email nullable
    op.add_column('users', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=True)

    # Recreate payments table and its indexes
    op.create_table(
        'payments',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('order_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('payment_method', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.uid'], name=op.f('payments_user_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('payments_pkey'))
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=True)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)

    # Recreate addresses table and its indexes
    op.create_table(
        'addresses',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_uid', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], name=op.f('addresses_user_uid_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('addresses_pkey')),
        sa.UniqueConstraint('user_uid', name=op.f('uc_user_address'))
    )
    op.create_index(op.f('ix_addresses_id'), 'addresses', ['id'], unique=False)
