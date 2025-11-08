"""Add content fields to rewrite_logs table

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add original_email and rewritten_email columns to rewrite_logs table
    op.add_column('rewrite_logs', sa.Column('original_email', sa.Text(), nullable=False, server_default=''))
    op.add_column('rewrite_logs', sa.Column('rewritten_email', sa.Text(), nullable=False, server_default=''))
    
    # Remove server defaults after adding columns (they were only for existing rows)
    # For new rows, these will be set by the application
    op.alter_column('rewrite_logs', 'original_email', server_default=None)
    op.alter_column('rewrite_logs', 'rewritten_email', server_default=None)


def downgrade() -> None:
    # Remove the content columns
    op.drop_column('rewrite_logs', 'rewritten_email')
    op.drop_column('rewrite_logs', 'original_email')

