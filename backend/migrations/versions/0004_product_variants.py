"""add product variants and order variant snapshots

Revision ID: 0004_product_variants
Revises: 0003_promotional_pricing
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_product_variants"
down_revision: str | None = "0003_promotional_pricing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_variant_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "product_id", "name", name="uq_product_variant_groups_name"
        ),
    )
    op.create_index(
        "ix_product_variant_groups_product_id",
        "product_variant_groups",
        ["product_id"],
    )
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "group_id",
            sa.Integer(),
            sa.ForeignKey("product_variant_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("price_delta", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "price_delta >= 0", name="ck_product_variants_price_delta_non_negative"
        ),
        sa.UniqueConstraint("group_id", "name", name="uq_product_variants_group_name"),
    )
    op.create_index("ix_product_variants_group_id", "product_variants", ["group_id"])
    op.create_table(
        "order_item_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_item_id",
            sa.Integer(),
            sa.ForeignKey("order_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("group_name", sa.String(80), nullable=False),
        sa.Column("variant_name", sa.String(120), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint(
            "unit_price >= 0", name="ck_order_item_variants_unit_price_non_negative"
        ),
    )
    op.create_index(
        "ix_order_item_variants_order_item_id",
        "order_item_variants",
        ["order_item_id"],
    )


def downgrade() -> None:
    op.drop_table("order_item_variants")
    op.drop_table("product_variants")
    op.drop_table("product_variant_groups")
