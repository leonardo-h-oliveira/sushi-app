from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category


def list_active(db: Session) -> list[Category]:
    statement = select(Category).where(Category.active.is_(True)).order_by(Category.name)
    return list(db.scalars(statement))


def get_by_id(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_by_name_or_slug(db: Session, name: str, slug: str) -> Category | None:
    statement = select(Category).where(
        (func.lower(Category.name) == name.lower()) | (Category.slug == slug)
    )
    return db.scalar(statement)


def save(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
