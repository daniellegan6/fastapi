"""add content column to post column

Revision ID: b732e0f4a190
Revises: f4a8ea8292a5
Create Date: 2025-07-08 18:51:59.261081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b732e0f4a190'
down_revision: Union[str, Sequence[str], None] = 'f4a8ea8292a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
