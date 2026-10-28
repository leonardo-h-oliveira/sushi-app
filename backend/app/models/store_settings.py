from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Integer, Numeric, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StoreSettings(Base):
    __tablename__ = "store_settings"
    __table_args__ = (
        CheckConstraint("delivery_enabled OR pickup_enabled", name="ck_store_settings_fulfillment"),
        CheckConstraint("pix_enabled OR card_on_delivery_enabled OR cash_enabled", name="ck_store_settings_payment"),
        CheckConstraint("delivery_fee >= 0", name="ck_store_settings_delivery_fee_non_negative"),
        CheckConstraint("minimum_order >= 0", name="ck_store_settings_minimum_order_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    delivery_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pickup_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pix_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    card_on_delivery_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cash_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("5.00"), nullable=False)
    minimum_order: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    operations_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_neighborhoods: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opening_hours: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    closed_dates: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    pix_instructions: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
