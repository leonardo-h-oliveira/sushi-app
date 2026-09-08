import re
import unicodedata

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories import categories as category_repository


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def list_active_categories(db: Session) -> list[Category]:
    return category_repository.list_active(db)


def create_category(db: Session, name: str) -> Category:
    slug = slugify(name)
    _ensure_unique(db, name, slug)
    return _save(db, Category(name=name, slug=slug))


def update_category(db: Session, category_id: int, name: str) -> Category:
    category = _get_or_404(db, category_id)
    slug = slugify(name)
    duplicate = category_repository.get_by_name_or_slug(db, name, slug)
    if duplicate and duplicate.id != category.id:
        _raise_duplicate()
    category.name = name
    category.slug = slug
    return _save(db, category)


def deactivate_category(db: Session, category_id: int) -> None:
    category = _get_or_404(db, category_id)
    category.active = False
    _save(db, category)


def _get_or_404(db: Session, category_id: int) -> Category:
    category = category_repository.get_by_id(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )
    return category


def _ensure_unique(db: Session, name: str, slug: str) -> None:
    if category_repository.get_by_name_or_slug(db, name, slug):
        _raise_duplicate()


def _save(db: Session, category: Category) -> Category:
    try:
        return category_repository.save(db, category)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists.",
        ) from error


def _raise_duplicate() -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="A category with this name already exists.",
    )
