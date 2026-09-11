from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.repositories import products as product_repository
from app.schemas.product import ProductCreate, ProductUpdate


def list_available_products(db: Session, category_slug: str | None) -> list[Product]:
    return product_repository.list_available(db, category_slug)


def get_available_product(db: Session, product_id: int) -> Product:
    product = product_repository.get_available(db, product_id)
    if product is None:
        _raise_not_found()
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    _require_category(db, payload.category_id)
    data = payload.model_dump()
    data["image_url"] = str(payload.image_url) if payload.image_url else None
    return _save(db, Product(**data))


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = product_repository.get_by_id(db, product_id)
    if product is None:
        _raise_not_found()

    changes = payload.model_dump(exclude_unset=True)
    if "category_id" in changes:
        _require_category(db, changes["category_id"])
    if "image_url" in changes and changes["image_url"] is not None:
        changes["image_url"] = str(changes["image_url"])
    _validate_promotional_price(
        changes.get("price", product.price),
        changes.get("original_price", product.original_price),
    )
    for field, value in changes.items():
        setattr(product, field, value)
    return _save(db, product)


def _validate_promotional_price(
    price: Decimal,
    original_price: Decimal | None,
) -> None:
    if original_price is not None and original_price <= price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Original price must be greater than the current price.",
        )


def _require_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The selected category does not exist.",
        )
    return category


def _save(db: Session, product: Product) -> Product:
    try:
        return product_repository.save(db, product)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The product could not be saved because it conflicts with existing data.",
        ) from error


def _raise_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found.",
    )
