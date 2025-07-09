"""Add slug to categories

Revision ID: 102ad414ed63
Revises: 29adf5987cd3
Create Date: 2025-06-26 11:11:22.831502
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '102ad414ed63'
down_revision: Union[str, None] = '29adf5987cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # 🔍 Check existing columns in 'categories'
    columns = [col["name"] for col in inspector.get_columns("categories")]

    # ✅ Step 1: Add column if not present
    if "slug" not in columns:
        op.add_column("categories", sa.Column("slug", sa.String(length=100)))

    # 🔄 Refresh the inspector after adding column
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("categories")]

    # ✅ Step 2: Populate slugs only if slug column exists
    if "slug" in columns:
        op.execute("UPDATE categories SET slug = LOWER(name)")

        # ✅ Step 3: Set NOT NULL only if it's currently nullable
        for col in inspector.get_columns("categories"):
            if col["name"] == "slug" and col["nullable"]:
                op.execute("ALTER TABLE categories ALTER COLUMN slug SET NOT NULL")
                break

    # ✅ Step 4: Add unique constraint if not present
    existing_constraints = [uc["name"] for uc in inspector.get_unique_constraints("categories")]
    if "uq_categories_slug" not in existing_constraints:
        op.create_unique_constraint("uq_categories_slug", "categories", ["slug"])


def downgrade() -> None:
    # Drop unique constraint if it exists
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_constraints = [uc["name"] for uc in inspector.get_unique_constraints("categories")]

    if "uq_categories_slug" in existing_constraints:
        op.drop_constraint("uq_categories_slug", "categories", type_="unique")

    # Drop slug column if it exists
    columns = [col["name"] for col in inspector.get_columns("categories")]
    if "slug" in columns:
        op.execute("ALTER TABLE categories DROP COLUMN slug")
