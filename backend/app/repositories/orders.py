from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem


def get_by_number(db: Session, number: str) -> Order | None:
    statement = (
        select(Order)
        .options(*_loads())
        .where(Order.number == number.upper())
    )
    return db.scalar(statement)


def list_orders(db: Session) -> list[Order]:
    statement = select(Order).options(*_loads()).order_by(Order.created_at.desc())
    return list(db.scalars(statement).all())


def _loads():
    return (
        selectinload(Order.items).selectinload(OrderItem.addons),
        selectinload(Order.customer),
        selectinload(Order.address),
    )


def save(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)
    return get_by_number(db, order.number) or order
