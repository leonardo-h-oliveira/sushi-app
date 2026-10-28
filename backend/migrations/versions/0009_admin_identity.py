"""Persist staff identities and revocable opaque sessions."""

from alembic import op
import sqlalchemy as sa

revision = "0009_admin_identity"
down_revision = "0008_store_operating_rules"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(300), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="admin"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("admin_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_admin_sessions_user_id", "admin_sessions", ["user_id"])
    op.create_index("ix_admin_sessions_expires_at", "admin_sessions", ["expires_at"])


def downgrade():
    op.drop_table("admin_sessions")
    op.drop_table("admin_users")
