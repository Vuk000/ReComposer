"""Initial migration: users and rewrite_logs tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create rewrite_logs table
    op.create_table(
        'rewrite_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tone', sa.String(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('token_used', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rewrite_logs_id'), 'rewrite_logs', ['id'], unique=False)
    op.create_index(op.f('ix_rewrite_logs_user_id'), 'rewrite_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_rewrite_logs_created_at'), 'rewrite_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop rewrite_logs table
    op.drop_index(op.f('ix_rewrite_logs_created_at'), table_name='rewrite_logs')
    op.drop_index(op.f('ix_rewrite_logs_user_id'), table_name='rewrite_logs')
    op.drop_index(op.f('ix_rewrite_logs_id'), table_name='rewrite_logs')
    op.drop_table('rewrite_logs')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

