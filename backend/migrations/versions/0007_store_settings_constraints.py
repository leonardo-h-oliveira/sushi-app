"""Enforce operational settings invariants in the database."""

from alembic import op

revision = "0007_store_settings_constraints"
down_revision = "0006_store_settings"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("store_settings") as batch:
        batch.create_check_constraint("ck_store_settings_fulfillment", "delivery_enabled OR pickup_enabled")
        batch.create_check_constraint("ck_store_settings_payment", "pix_enabled OR card_on_delivery_enabled OR cash_enabled")


def downgrade():
    with op.batch_alter_table("store_settings") as batch:
        batch.drop_constraint("ck_store_settings_payment", type_="check")
        batch.drop_constraint("ck_store_settings_fulfillment", type_="check")
