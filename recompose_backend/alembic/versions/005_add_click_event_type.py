"""Add CLICK event type to EventType enum

Revision ID: 005
Revises: 004
Create Date: 2024-01-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add CLICK to EventType enum
    # PostgreSQL enum modification
    op.execute("""
        ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'CLICK';
    """)


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum type
    # For now, we'll leave CLICK in the enum
    pass

