"""Alter payments.created_at to be timezone-aware

Revision ID: 9fa654bd9d02
Revises: bced1bc6c74c
Create Date: 2025-06-16 09:56:24.969212
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9fa654bd9d02'
down_revision: Union[str, None] = 'bced1bc6c74c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alter `created_at` to be timezone-aware (TIMESTAMP WITH TIME ZONE)
    op.alter_column(
        'payments',
        'created_at',
        type_=sa.TIMESTAMP(timezone=True),
        existing_type=sa.TIMESTAMP(timezone=False),
        postgresql_using="created_at AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert `created_at` back to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column(
        'payments',
        'created_at',
        type_=sa.TIMESTAMP(timezone=False),
        existing_type=sa.TIMESTAMP(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'"
    )
