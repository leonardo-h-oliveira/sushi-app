from datetime import datetime
from decimal import Decimal
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderItemAddon, OrderItemVariant
from app.models.product import Product
from app.repositories import orders as order_repository
from app.models.enums import OrderStatus
from app.schemas.order import OrderCreate


DELIVERY_FEE = Decimal("5.00")


def create_order(db: Session, payload: OrderCreate) -> Order:
    customer = Customer(name=payload.customer_name.strip(), phone=payload.phone.strip())
    address = Address(**payload.address.model_dump()) if payload.address else None
    if address:
        customer.addresses.append(address)

    subtotal = Decimal("0.00")
    order_items: list[OrderItem] = []
    for item_input in payload.items:
        product = db.get(Product, item_input.product_id)
        if product is None or not product.active or not product.category.active:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="One of the selected products is unavailable.")
        selected_addons = {addon.id: addon for addon in product.addons if addon.active}
        addons = []
        for addon_id in set(item_input.addon_ids):
            addon = selected_addons.get(addon_id)
            if addon is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="One of the selected add-ons is unavailable.")
            addons.append(OrderItemAddon(addon_name=addon.name, unit_price=addon.price_delta))
        variants = _selected_variants(product, item_input.variant_ids)
        option_total = sum(
            (option.unit_price for option in [*addons, *variants]), Decimal("0.00")
        )
        unit_price = product.price + option_total
        item_total = unit_price * item_input.quantity
        subtotal += item_total
        order_items.append(OrderItem(product=product, product_name=product.name, quantity=item_input.quantity, unit_price=unit_price, total=item_total, notes=item_input.notes, addons=addons, variants=variants))

    delivery_fee = DELIVERY_FEE if payload.fulfillment_method.value == "delivery" else Decimal("0.00")
    order = Order(number=_order_number(), customer=customer, address=address, fulfillment_method=payload.fulfillment_method, payment_method=payload.payment_method, notes=payload.notes, subtotal=subtotal, delivery_fee=delivery_fee, total=subtotal + delivery_fee, items=order_items)
    return order_repository.save(db, order)


def _selected_variants(product: Product, variant_ids: list[int]) -> list[OrderItemVariant]:
    if len(variant_ids) != len(set(variant_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A product variant cannot be selected more than once.",
        )

    groups = [group for group in product.variant_groups if group.active]
    available = {
        variant.id: (group, variant)
        for group in groups
        for variant in group.variants
        if variant.active
    }
    selected_by_group: dict[int, tuple] = {}
    snapshots: list[OrderItemVariant] = []
    for variant_id in variant_ids:
        selection = available.get(variant_id)
        if selection is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="One of the selected product variants is unavailable.",
            )
        group, variant = selection
        if group.id in selected_by_group:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Choose only one option for {group.name}.",
            )
        selected_by_group[group.id] = selection
        snapshots.append(
            OrderItemVariant(
                group_name=group.name,
                variant_name=variant.name,
                unit_price=variant.price_delta,
            )
        )

    missing = [group.name for group in groups if group.required and group.id not in selected_by_group]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Choose an option for: {', '.join(missing)}.",
        )
    return snapshots


def get_order(db: Session, number: str) -> Order:
    order = order_repository.get_by_number(db, number)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


def list_orders(db: Session) -> list[Order]:
    return order_repository.list_orders(db)


def update_status(db: Session, number: str, new_status: OrderStatus) -> Order:
    order = get_order(db, number)
    order.status = new_status
    db.commit()
    return get_order(db, order.number)


def _order_number() -> str:
    return f"SP{datetime.now():%y%m%d}-{secrets.token_hex(3).upper()}"
