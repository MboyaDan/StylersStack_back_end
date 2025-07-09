"""Change Order.id from Integer to String

Revision ID: 64f1ee018e71
Revises: 7c8ff88d4a45
Create Date: 2025-07-09 11:13:36.576032
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64f1ee018e71'
down_revision = '7c8ff88d4a45'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraints
    op.drop_constraint('order_items_order_id_fkey', 'order_items', type_='foreignkey')
    op.drop_constraint('payments_order_id_key', 'payments', type_='unique')
    op.drop_constraint('payments_order_id_fkey', 'payments', type_='foreignkey')

    # Alter foreign key columns first
    op.alter_column('order_items', 'order_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    postgresql_using="order_id::text")

    op.alter_column('payments', 'order_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    postgresql_using="order_id::text")

    # Alter orders.id column
    op.alter_column('orders', 'id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    postgresql_using="id::text")

    # Restore constraints
    op.create_foreign_key('order_items_order_id_fkey', 'order_items', 'orders', ['order_id'], ['id'])
    op.create_foreign_key('payments_order_id_fkey', 'payments', 'orders', ['order_id'], ['id'])
    op.create_unique_constraint('payments_order_id_key', 'payments', ['order_id'])


def downgrade():
    raise NotImplementedError("Downgrade is not supported due to non-integer order IDs.")
