"""Persist structured cash change instructions."""
from alembic import op
import sqlalchemy as sa

revision = "0010_cash_change"
down_revision = "0009_admin_identity"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders") as batch:
        batch.add_column(sa.Column("cash_change_for", sa.Numeric(10, 2), nullable=True))


def downgrade():
    with op.batch_alter_table("orders") as batch:
        batch.drop_column("cash_change_for")
