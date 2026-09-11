from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.order import OrderItem


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        CheckConstraint(
            "original_price IS NULL OR original_price > price",
            name="ck_products_original_price_above_price",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    addons: Mapped[list["ProductAddon"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    variant_groups: Mapped[list["ProductVariantGroup"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariantGroup.sort_order",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")

    @property
    def discount_percent(self) -> int | None:
        if self.original_price is None:
            return None
        return round((1 - self.price / self.original_price) * 100)


class ProductAddon(Base):
    __tablename__ = "product_addons"
    __table_args__ = (
        UniqueConstraint("product_id", "name", name="uq_product_addons_product_name"),
        CheckConstraint(
            "price_delta >= 0", name="ck_product_addons_price_delta_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_delta: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="addons")


class ProductVariantGroup(Base):
    """A single-choice product option such as flavor or size."""

    __tablename__ = "product_variant_groups"
    __table_args__ = (
        UniqueConstraint("product_id", "name", name="uq_product_variant_groups_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="variant_groups")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="ProductVariant.sort_order",
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("group_id", "name", name="uq_product_variants_group_name"),
        CheckConstraint(
            "price_delta >= 0", name="ck_product_variants_price_delta_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("product_variant_groups.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_delta: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    group: Mapped["ProductVariantGroup"] = relationship(back_populates="variants")
