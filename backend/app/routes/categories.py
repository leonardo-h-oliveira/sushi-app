from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import categories as category_service


router = APIRouter(tags=["Categories"])
DatabaseSession = Annotated[Session, Depends(get_db)]
Administrator = Annotated[None, Depends(require_admin)]


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: DatabaseSession):
    return category_service.list_active_categories(db)


@router.post(
    "/admin/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(payload: CategoryCreate, db: DatabaseSession, _: Administrator):
    return category_service.create_category(db, payload.name)


@router.patch("/admin/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: DatabaseSession,
    _: Administrator,
):
    return category_service.update_category(db, category_id, payload.name)


@router.delete(
    "/admin/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_category(category_id: int, db: DatabaseSession, _: Administrator):
    category_service.deactivate_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
