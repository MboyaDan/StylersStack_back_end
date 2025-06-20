"""Re-add payments and addresses tables

Revision ID: ea316710e0db
Revises: 017396d5ede1
Create Date: 2025-06-18 10:03:02.716005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea316710e0db'
down_revision: Union[str, None] = '017396d5ede1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('user_product_unique', 'favorites', ['user_uid', 'product_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('user_product_unique', 'favorites', type_='unique')
    # ### end Alembic commands ###
"""Re-add payments and addresses tables

Revision ID: ea316710e0db
Revises: 017396d5ede1
Create Date: 2025-06-18 10:03:02.716005
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'ea316710e0db'
down_revision: Union[str, None] = '017396d5ede1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'user_product_unique'
    """))

    if not result.scalar():
        op.create_unique_constraint(
            'user_product_unique',
            'favorites',
            ['user_uid', 'product_id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('user_product_unique', 'favorites', type_='unique')
