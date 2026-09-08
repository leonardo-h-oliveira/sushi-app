from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import FulfillmentMethod, OrderStatus, PaymentMethod


class AddressInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    street: str = Field(min_length=2, max_length=160)
    number: str = Field(min_length=1, max_length=20)
    neighborhood: str = Field(min_length=2, max_length=100)
    complement: str | None = Field(default=None, max_length=160)
    city: str = Field(default="Poços de Caldas", min_length=2, max_length=100)
    state: str = Field(default="MG", min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=12)


class OrderItemInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=99)
    addon_ids: list[int] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=300)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=30)
    fulfillment_method: FulfillmentMethod
    payment_method: PaymentMethod
    address: AddressInput | None = None
    notes: str | None = Field(default=None, max_length=500)
    items: list[OrderItemInput] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_delivery_address(self):
        if self.fulfillment_method == FulfillmentMethod.DELIVERY and self.address is None:
            raise ValueError("An address is required for delivery orders.")
        return self


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_name: str
    quantity: int
    unit_price: Decimal
    total: Decimal
    notes: str | None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str
    status: OrderStatus
    fulfillment_method: FulfillmentMethod
    payment_method: PaymentMethod
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]
    customer_name: str | None = None
    phone: str | None = None
    address: AddressInput | None = None
    notes: str | None = None

    @classmethod
    def from_model(cls, order):
        data = cls.model_validate(order)
        data.customer_name = order.customer.name if order.customer else None
        data.phone = order.customer.phone if order.customer else None
        data.address = AddressInput.model_validate(order.address) if order.address else None
        data.notes = order.notes
        return data


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
