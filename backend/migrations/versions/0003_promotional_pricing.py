"""add promotional product pricing

Revision ID: 0003_promotional_pricing
Revises: 0002_menu_sort_order
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_promotional_pricing"
down_revision: str | None = "0002_menu_sort_order"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(sa.Column("original_price", sa.Numeric(10, 2)))
        batch_op.create_check_constraint(
            "ck_products_original_price_above_price",
            "original_price IS NULL OR original_price > price",
        )


def downgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint(
            "ck_products_original_price_above_price", type_="check"
        )
        batch_op.drop_column("original_price")
