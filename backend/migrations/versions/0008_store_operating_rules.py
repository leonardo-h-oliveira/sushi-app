"""Add restaurant-controlled delivery areas and opening hours."""

from alembic import op
import sqlalchemy as sa

revision = "0008_store_operating_rules"
down_revision = "0007_store_settings_constraints"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("store_settings") as batch:
        batch.add_column(sa.Column("operations_ready", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("delivery_neighborhoods", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("schedule_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("opening_hours", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("closed_dates", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("pix_instructions", sa.String(1000), nullable=False, server_default=""))


def downgrade():
    with op.batch_alter_table("store_settings") as batch:
        for name in ["pix_instructions", "closed_dates", "opening_hours", "schedule_enabled", "delivery_neighborhoods", "operations_ready"]:
            batch.drop_column(name)
