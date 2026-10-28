from decimal import Decimal
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OpeningWindow(BaseModel):
    weekday: int = Field(ge=0, le=6)
    opens: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    closes: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")

    @model_validator(mode="after")
    def distinct_times(self):
        if self.opens == self.closes:
            raise ValueError("Opening and closing times must differ.")
        return self


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
    operations_ready: bool
    delivery_neighborhoods: list[str]
    schedule_enabled: bool
    opening_hours: list[OpeningWindow]
    closed_dates: list[date]
    pix_instructions: str
    next_opening: str | None = None


class StoreSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_open: bool | None = None
    delivery_enabled: bool | None = None
    pickup_enabled: bool | None = None
    pix_enabled: bool | None = None
    card_on_delivery_enabled: bool | None = None
    cash_enabled: bool | None = None
    delivery_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    minimum_order: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    operations_ready: bool | None = None
    delivery_neighborhoods: list[str] | None = Field(default=None, max_length=300)
    schedule_enabled: bool | None = None
    opening_hours: list[OpeningWindow] | None = Field(default=None, max_length=28)
    closed_dates: list[date] | None = Field(default=None, max_length=366)
    pix_instructions: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one store setting must be provided.")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Store settings cannot be null.")
        if self.delivery_neighborhoods is not None:
            self.delivery_neighborhoods = list(dict.fromkeys(name.strip() for name in self.delivery_neighborhoods))
            if any(len(name) < 2 or len(name) > 100 for name in self.delivery_neighborhoods):
                raise ValueError("Each neighborhood must contain 2 to 100 characters.")
        return self
