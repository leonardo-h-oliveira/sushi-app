"""add store settings

Revision ID: 0006_store_settings
Revises: 0005_secure_order_tracking
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0006_store_settings"
down_revision: str | None = "0005_secure_order_tracking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table = op.create_table(
        "store_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_open", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("delivery_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("pickup_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("pix_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("card_on_delivery_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("cash_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=False, server_default="5.00"),
        sa.Column("minimum_order", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.CheckConstraint("delivery_fee >= 0", name="ck_store_settings_delivery_fee_non_negative"),
        sa.CheckConstraint("minimum_order >= 0", name="ck_store_settings_minimum_order_non_negative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(table, [{"id": 1}])


def downgrade() -> None:
    op.drop_table("store_settings")
