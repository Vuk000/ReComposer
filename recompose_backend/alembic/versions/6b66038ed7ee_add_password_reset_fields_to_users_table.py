"""Add password reset fields to users table

Revision ID: 6b66038ed7ee
Revises: 005
Create Date: 2025-11-21 18:44:03.125020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b66038ed7ee'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password reset fields to users table
    op.add_column('users', sa.Column('password_reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_users_password_reset_token'), 'users', ['password_reset_token'], unique=False)


def downgrade() -> None:
    # Remove password reset fields
    op.drop_index(op.f('ix_users_password_reset_token'), table_name='users')
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'password_reset_token')
