from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services import products as product_service


router = APIRouter(tags=["Products"])
DatabaseSession = Annotated[Session, Depends(get_db)]
Administrator = Annotated[None, Depends(require_admin)]


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    db: DatabaseSession,
    category: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
):
    return product_service.list_available_products(db, category)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: DatabaseSession):
    return product_service.get_available_product(db, product_id)


@router.post(
    "/admin/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(payload: ProductCreate, db: DatabaseSession, _: Administrator):
    return product_service.create_product(db, payload)


@router.patch("/admin/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: DatabaseSession,
    _: Administrator,
):
    return product_service.update_product(db, product_id, payload)
