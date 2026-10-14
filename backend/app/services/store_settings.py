from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.store_settings import StoreSettings
from app.schemas.store_settings import StoreSettingsUpdate


def get_settings(db: Session) -> StoreSettings:
    settings = db.get(StoreSettings, 1)
    if settings is None:
        settings = StoreSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, payload: StoreSettingsUpdate) -> StoreSettings:
    settings = get_settings(db)
    changes = payload.model_dump(exclude_unset=True)
    resulting = {field: changes.get(field, getattr(settings, field)) for field in (
        "delivery_enabled", "pickup_enabled", "pix_enabled", "card_on_delivery_enabled", "cash_enabled"
    )}
    if not (resulting["delivery_enabled"] or resulting["pickup_enabled"]):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Enable delivery or pickup.")
    if not (resulting["pix_enabled"] or resulting["card_on_delivery_enabled"] or resulting["cash_enabled"]):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Enable at least one payment method.")
    for field, value in changes.items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
