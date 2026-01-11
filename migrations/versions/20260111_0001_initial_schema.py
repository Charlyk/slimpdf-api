"""Initial database schema

Revision ID: 0001
Revises:
Create Date: 2026-01-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table (Auth.js compatible)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), unique=True, nullable=True),
        sa.Column('email_verified', sa.DateTime(timezone=True), nullable=True),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('password_hash', sa.Text(), nullable=True),
        sa.Column('plan', sa.String(20), server_default='free', nullable=False),
        sa.Column('stripe_customer_id', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Accounts table (Auth.js compatible)
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('provider', sa.Text(), nullable=False),
        sa.Column('provider_account_id', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('token_type', sa.Text(), nullable=True),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('id_token', sa.Text(), nullable=True),
        sa.Column('session_state', sa.Text(), nullable=True),
        sa.UniqueConstraint('provider', 'provider_account_id'),
    )
    op.create_index('idx_accounts_user', 'accounts', ['user_id'])

    # Sessions table (Auth.js compatible)
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_token', sa.Text(), unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_sessions_user', 'sessions', ['user_id'])

    # Verification tokens table (Auth.js compatible)
    op.create_table(
        'verification_tokens',
        sa.Column('identifier', sa.Text(), primary_key=True),
        sa.Column('token', sa.Text(), primary_key=True),
        sa.Column('expires', sa.DateTime(timezone=True), nullable=False),
    )

    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stripe_subscription_id', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('plan_interval', sa.Text(), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key_hash', sa.Text(), nullable=False),
        sa.Column('key_prefix', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), server_default='Default', nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'])

    # Usage logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tool', sa.Text(), nullable=False),
        sa.Column('input_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('output_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('file_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('api_request', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ip_address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_usage_logs_user_created', 'usage_logs', ['user_id', 'created_at'])
    op.create_index('idx_usage_logs_created', 'usage_logs', ['created_at'])

    # Jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tool', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), server_default='pending', nullable=False),
        sa.Column('input_filename', sa.Text(), nullable=True),
        sa.Column('output_filename', sa.Text(), nullable=True),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('original_size', sa.BigInteger(), nullable=True),
        sa.Column('output_size', sa.BigInteger(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_jobs_user', 'jobs', ['user_id'])
    op.create_index('idx_jobs_expires', 'jobs', ['expires_at'])


def downgrade() -> None:
    op.drop_table('jobs')
    op.drop_table('usage_logs')
    op.drop_table('api_keys')
    op.drop_table('subscriptions')
    op.drop_table('verification_tokens')
    op.drop_table('sessions')
    op.drop_table('accounts')
    op.drop_table('users')
