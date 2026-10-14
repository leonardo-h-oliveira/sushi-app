from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StoreSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_open: bool
    delivery_enabled: bool
    pickup_enabled: bool
    pix_enabled: bool
    card_on_delivery_enabled: bool
    cash_enabled: bool
    delivery_fee: Decimal
    minimum_order: Decimal


class StoreSettingsUpdate(BaseModel):
    is_open: bool | None = None
    delivery_enabled: bool | None = None
    pickup_enabled: bool | None = None
    pix_enabled: bool | None = None
    card_on_delivery_enabled: bool | None = None
    cash_enabled: bool | None = None
    delivery_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    minimum_order: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one store setting must be provided.")
        return self
