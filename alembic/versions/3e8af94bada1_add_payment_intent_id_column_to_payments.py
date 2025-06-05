"""Add payment_intent_id column to payments

Revision ID: 3e8af94bada1
Revises: 5bf002d16396
Create Date: 2025-06-05 11:14:06.772118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e8af94bada1'
down_revision: Union[str, None] = '5bf002d16396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payments', sa.Column('payment_intent_id', sa.String(), unique=True, nullable=True))

def downgrade() -> None:
    op.drop_column('payments', 'payment_intent_id')
