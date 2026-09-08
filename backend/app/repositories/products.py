from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.product import Product


def list_available(db: Session, category_slug: str | None = None) -> list[Product]:
    statement = (
        select(Product)
        .join(Product.category)
        .options(selectinload(Product.category))
        .where(Product.active.is_(True), Category.active.is_(True))
        .order_by(Category.name, Product.name)
    )
    if category_slug:
        statement = statement.where(Category.slug == category_slug.lower())
    return list(db.scalars(statement))


def get_available(db: Session, product_id: int) -> Product | None:
    statement = (
        select(Product)
        .join(Product.category)
        .options(selectinload(Product.category))
        .where(
            Product.id == product_id,
            Product.active.is_(True),
            Category.active.is_(True),
        )
    )
    return db.scalar(statement)


def get_by_id(db: Session, product_id: int) -> Product | None:
    statement = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id)
    )
    return db.scalar(statement)


def save(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return get_by_id(db, product.id) or product
