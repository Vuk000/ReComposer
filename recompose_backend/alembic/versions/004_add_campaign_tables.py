"""Add campaign tables and update subscription plans

Revision ID: 004
Revises: 003
Create Date: 2024-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update users table: add trial_end_date, migrate subscription_plan values
    op.add_column('users', sa.Column('trial_end_date', sa.DateTime(), nullable=True))
    
    # Migrate subscription_plan values: "free" -> "standard", remove "enterprise"
    op.execute("""
        UPDATE users 
        SET subscription_plan = 'standard' 
        WHERE subscription_plan = 'free'
    """)
    op.execute("""
        UPDATE users 
        SET subscription_plan = 'standard' 
        WHERE subscription_plan = 'enterprise'
    """)
    
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_user_id'), 'contacts', ['user_id'], unique=False)
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=False)
    op.create_index('ix_contacts_user_email', 'contacts', ['user_id', 'email'], unique=False)
    
    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('Draft', 'Running', 'Paused', 'Completed', 'Cancelled', name='campaignstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('launched_at', sa.DateTime(), nullable=True),
        sa.Column('paused_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_user_id'), 'campaigns', ['user_id'], unique=False)
    op.create_index(op.f('ix_campaigns_status'), 'campaigns', ['status'], unique=False)
    
    # Create campaign_emails table
    op.create_table(
        'campaign_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('delay_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delay_hours', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_emails_id'), 'campaign_emails', ['id'], unique=False)
    op.create_index(op.f('ix_campaign_emails_campaign_id'), 'campaign_emails', ['campaign_id'], unique=False)
    
    # Create campaign_recipients table
    op.create_table(
        'campaign_recipients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('Pending', 'Sent', 'Replied', 'Bounced', 'Failed', 'Skipped', name='recipientstatus'), nullable=False),
        sa.Column('last_sent_at', sa.DateTime(), nullable=True),
        sa.Column('next_send_at', sa.DateTime(), nullable=True),
        sa.Column('tracking_id', sa.String(), nullable=True),
        sa.Column('sent_message_id', sa.String(), nullable=True),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reply_detected_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_recipients_id'), 'campaign_recipients', ['id'], unique=False)
    op.create_index(op.f('ix_campaign_recipients_campaign_id'), 'campaign_recipients', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_campaign_recipients_contact_id'), 'campaign_recipients', ['contact_id'], unique=False)
    op.create_index(op.f('ix_campaign_recipients_status'), 'campaign_recipients', ['status'], unique=False)
    op.create_index(op.f('ix_campaign_recipients_next_send_at'), 'campaign_recipients', ['next_send_at'], unique=False)
    op.create_index(op.f('ix_campaign_recipients_tracking_id'), 'campaign_recipients', ['tracking_id'], unique=True)
    
    # Create email_events table
    op.create_table(
        'email_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_recipient_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.Enum('OPEN', 'REPLY', name='eventtype'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['campaign_recipient_id'], ['campaign_recipients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_events_id'), 'email_events', ['id'], unique=False)
    op.create_index(op.f('ix_email_events_campaign_recipient_id'), 'email_events', ['campaign_recipient_id'], unique=False)
    op.create_index(op.f('ix_email_events_event_type'), 'email_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_email_events_timestamp'), 'email_events', ['timestamp'], unique=False)
    
    # Create email_accounts table
    op.create_table(
        'email_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('gmail', 'outlook', 'smtp', name='emailprovider'), nullable=False),
        sa.Column('email_address', sa.String(), nullable=False),
        sa.Column('encrypted_oauth_token', sa.String(), nullable=True),
        sa.Column('encrypted_refresh_token', sa.String(), nullable=True),
        sa.Column('smtp_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_accounts_id'), 'email_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_email_accounts_user_id'), 'email_accounts', ['user_id'], unique=False)
    op.create_index(op.f('ix_email_accounts_provider'), 'email_accounts', ['provider'], unique=False)


def downgrade() -> None:
    # Drop new tables in reverse order
    op.drop_index(op.f('ix_email_accounts_provider'), table_name='email_accounts')
    op.drop_index(op.f('ix_email_accounts_user_id'), table_name='email_accounts')
    op.drop_index(op.f('ix_email_accounts_id'), table_name='email_accounts')
    op.drop_table('email_accounts')
    
    op.drop_index(op.f('ix_email_events_timestamp'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_event_type'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_campaign_recipient_id'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_id'), table_name='email_events')
    op.drop_table('email_events')
    
    op.drop_index(op.f('ix_campaign_recipients_tracking_id'), table_name='campaign_recipients')
    op.drop_index(op.f('ix_campaign_recipients_next_send_at'), table_name='campaign_recipients')
    op.drop_index(op.f('ix_campaign_recipients_status'), table_name='campaign_recipients')
    op.drop_index(op.f('ix_campaign_recipients_contact_id'), table_name='campaign_recipients')
    op.drop_index(op.f('ix_campaign_recipients_campaign_id'), table_name='campaign_recipients')
    op.drop_index(op.f('ix_campaign_recipients_id'), table_name='campaign_recipients')
    op.drop_table('campaign_recipients')
    
    op.drop_index(op.f('ix_campaign_emails_campaign_id'), table_name='campaign_emails')
    op.drop_index(op.f('ix_campaign_emails_id'), table_name='campaign_emails')
    op.drop_table('campaign_emails')
    
    op.drop_index(op.f('ix_campaigns_status'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_user_id'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')
    
    op.drop_index('ix_contacts_user_email', table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_user_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')
    
    # Remove trial_end_date column
    op.drop_column('users', 'trial_end_date')
    
    # Note: We don't reverse the subscription_plan migration as it's data migration
    # If needed, manual intervention would be required

