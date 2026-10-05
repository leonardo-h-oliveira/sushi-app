"""add secure order tracking tokens

Revision ID: 0005_secure_order_tracking
Revises: 0004_product_variants
"""

from collections.abc import Sequence
import secrets

from alembic import op
import sqlalchemy as sa


revision: str = "0005_secure_order_tracking"
down_revision: str | None = "0004_product_variants"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("tracking_token", sa.String(64), nullable=True))
    orders = sa.table(
        "orders",
        sa.column("id", sa.Integer),
        sa.column("tracking_token", sa.String),
    )
    connection = op.get_bind()
    for order_id in connection.execute(sa.select(orders.c.id)).scalars():
        connection.execute(
            orders.update()
            .where(orders.c.id == order_id)
            .values(tracking_token=secrets.token_urlsafe(24))
        )
    with op.batch_alter_table("orders") as batch_op:
        batch_op.alter_column(
            "tracking_token", existing_type=sa.String(64), nullable=False
        )
    op.create_index(
        "ix_orders_tracking_token", "orders", ["tracking_token"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_orders_tracking_token", table_name="orders")
    op.drop_column("orders", "tracking_token")
