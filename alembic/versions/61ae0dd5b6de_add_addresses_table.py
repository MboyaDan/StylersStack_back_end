from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61ae0dd5b6de'
down_revision: Union[str, None] = '3ac9319bf4eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_uid', sa.String, sa.ForeignKey('users.uid'), nullable=False),
        sa.Column('address', sa.String(255), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('addresses')
    # Note: If you have a UniqueConstraint, you might need to drop it separately
    # op.drop_constraint('uc_user_address', 'addresses', type_='unique')