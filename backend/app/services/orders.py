from datetime import datetime
from decimal import Decimal
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderItemAddon
from app.models.product import Product
from app.repositories import orders as order_repository
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
        for addon_id in item_input.addon_ids:
            addon = selected_addons.get(addon_id)
            if addon is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="One of the selected add-ons is unavailable.")
            addons.append(OrderItemAddon(addon_name=addon.name, unit_price=addon.price_delta))
        unit_price = product.price + sum((addon.unit_price for addon in addons), Decimal("0.00"))
        item_total = unit_price * item_input.quantity
        subtotal += item_total
        order_items.append(OrderItem(product=product, product_name=product.name, quantity=item_input.quantity, unit_price=unit_price, total=item_total, notes=item_input.notes, addons=addons))

    delivery_fee = DELIVERY_FEE if payload.fulfillment_method.value == "delivery" else Decimal("0.00")
    order = Order(number=_order_number(), customer=customer, address=address, fulfillment_method=payload.fulfillment_method, payment_method=payload.payment_method, notes=payload.notes, subtotal=subtotal, delivery_fee=delivery_fee, total=subtotal + delivery_fee, items=order_items)
    return order_repository.save(db, order)


def get_order(db: Session, number: str) -> Order:
    order = order_repository.get_by_number(db, number)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


def _order_number() -> str:
    return f"SP{datetime.now():%y%m%d}-{secrets.token_hex(3).upper()}"
