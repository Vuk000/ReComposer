"""Add subscription fields to users table

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add subscription fields to users table
    op.add_column('users', sa.Column('subscription_plan', sa.String(), nullable=False, server_default='free'))
    op.add_column('users', sa.Column('subscription_status', sa.String(), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(), nullable=True))
    
    # Remove server defaults after adding columns (they were only for existing rows)
    # For new rows, these will be set by the application
    op.alter_column('users', 'subscription_plan', server_default=None)
    op.alter_column('users', 'subscription_status', server_default=None)


def downgrade() -> None:
    # Remove subscription fields
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'subscription_plan')

