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
    get_settings(db)
    # Serialize changes to the singleton on PostgreSQL so cross-field validation
    # cannot observe stale values from another administrator's transaction.
    settings = db.get(StoreSettings, 1, with_for_update=True, populate_existing=True)
    changes = payload.model_dump(exclude_unset=True, mode="json")
    resulting_value = lambda field: changes.get(field, getattr(settings, field))
    if resulting_value("schedule_enabled") and not resulting_value("opening_hours"):
        raise HTTPException(status_code=422, detail="Configure opening hours before enabling the schedule.")
    if resulting_value("operations_ready"):
        if resulting_value("delivery_enabled") and not resulting_value("delivery_neighborhoods"):
            raise HTTPException(status_code=422, detail="Configure delivery neighborhoods before enabling live orders.")
        if resulting_value("pix_enabled") and not resulting_value("pix_instructions").strip():
            raise HTTPException(status_code=422, detail="Configure PIX instructions before enabling live orders.")
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
