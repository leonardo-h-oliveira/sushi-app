from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import require_admin
from app.schemas.order import AddressInput, OrderCreate, OrderResponse, OrderStatusUpdate
from app.services import orders as order_service


router = APIRouter(prefix="/orders", tags=["Orders"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: DatabaseSession):
    return _response(order_service.create_order(db, payload))


@router.get("/{number}", response_model=OrderResponse)
def get_order(number: str, db: DatabaseSession):
    return _response(order_service.get_order(db, number))


@router.get("", response_model=list[OrderResponse], dependencies=[Depends(require_admin)])
def list_orders(db: DatabaseSession):
    return [_response(order) for order in order_service.list_orders(db)]


@router.patch("/{number}/status", response_model=OrderResponse, dependencies=[Depends(require_admin)])
def update_order_status(number: str, payload: OrderStatusUpdate, db: DatabaseSession):
    return _response(order_service.update_status(db, number, payload.status))


def _response(order):
    response = OrderResponse.model_validate(
        {
            "number": order.number,
            "status": order.status,
            "fulfillment_method": order.fulfillment_method,
            "payment_method": order.payment_method,
            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total": order.total,
            "created_at": order.created_at,
            "items": order.items,
        }
    )
    response.customer_name = order.customer.name if order.customer else None
    response.phone = order.customer.phone if order.customer else None
    response.address = AddressInput.model_validate(order.address) if order.address else None
    response.notes = order.notes
    return response
