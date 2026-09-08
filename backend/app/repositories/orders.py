from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem


def get_by_number(db: Session, number: str) -> Order | None:
    statement = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.addons))
        .where(Order.number == number.upper())
    )
    return db.scalar(statement)


def save(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)
    return get_by_number(db, order.number) or order
