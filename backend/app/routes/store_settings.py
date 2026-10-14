from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.store_settings import StoreSettingsResponse, StoreSettingsUpdate
from app.services import store_settings as settings_service


router = APIRouter(tags=["Store settings"])
DatabaseSession = Annotated[Session, Depends(get_db)]
Administrator = Annotated[None, Depends(require_admin)]


@router.get("/store-settings", response_model=StoreSettingsResponse)
def get_store_settings(db: DatabaseSession):
    return settings_service.get_settings(db)


@router.get("/admin/store-settings", response_model=StoreSettingsResponse)
def get_admin_store_settings(db: DatabaseSession, _: Administrator):
    return settings_service.get_settings(db)


@router.patch("/admin/store-settings", response_model=StoreSettingsResponse)
def update_store_settings(payload: StoreSettingsUpdate, db: DatabaseSession, _: Administrator):
    return settings_service.update_settings(db, payload)
