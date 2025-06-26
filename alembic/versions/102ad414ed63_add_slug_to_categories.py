"""Add slug to categories

Revision ID: 102ad414ed63
Revises: 29adf5987cd3
Create Date: 2025-06-26 11:11:22.831502
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, text


# revision identifiers, used by Alembic.
revision: str = '102ad414ed63'
down_revision: Union[str, None] = '29adf5987cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the column as nullable
    op.add_column('categories', sa.Column('slug', sa.String(length=100), nullable=True))

    # Step 2: Update existing rows (assuming name is lowercase and slug-safe)
    # You can customize the slug logic if needed
    op.execute("UPDATE categories SET slug = LOWER(name)")

    # Step 3: Alter to NOT NULL
    op.alter_column('categories', 'slug', nullable=False)

    # Step 4: Add unique constraint
    op.create_unique_constraint('uq_categories_slug', 'categories', ['slug'])


def downgrade() -> None:
    op.drop_constraint('uq_categories_slug', 'categories', type_='unique')
    op.drop_column('categories', 'slug')
