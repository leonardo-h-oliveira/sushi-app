from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services import orders as order_service


router = APIRouter(prefix="/orders", tags=["Orders"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: DatabaseSession):
    return order_service.create_order(db, payload)


@router.get("/{number}", response_model=OrderResponse)
def get_order(number: str, db: DatabaseSession):
    return order_service.get_order(db, number)
