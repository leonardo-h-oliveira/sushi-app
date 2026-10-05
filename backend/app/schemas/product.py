from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class ProductFields(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    original_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    image_url: HttpUrl | None = None
    category_id: int = Field(gt=0)
    active: bool = True

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Product name must contain at least two characters.")
        return normalized

    @model_validator(mode="after")
    def validate_promotional_price(self):
        if self.original_price is not None and self.original_price <= self.price:
            raise ValueError("Original price must be greater than the current price.")
        return self


class ProductCreate(ProductFields):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    original_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    image_url: HttpUrl | None = None
    category_id: int | None = Field(default=None, gt=0)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Product name must contain at least two characters.")
        return normalized

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one product field must be provided.")
        return self


class ProductCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ProductAddonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_delta: Decimal
    active: bool


class ProductOptionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    price_delta: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    active: bool = True

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Option name must contain at least two characters.")
        return normalized


class ProductOptionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    price_delta: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Option name must contain at least two characters.")
        return normalized

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one option field must be provided.")
        return self


class VariantGroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    required: bool = True
    active: bool = True

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Variant group name must contain at least two characters.")
        return normalized


class VariantGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    required: bool | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Variant group name must contain at least two characters.")
        return normalized

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one variant group field must be provided.")
        return self


class ProductVariantResponse(ProductAddonResponse):
    pass


class ProductVariantGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    required: bool
    active: bool
    variants: list[ProductVariantResponse] = Field(default_factory=list)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: Decimal
    original_price: Decimal | None
    discount_percent: int | None
    image_url: str | None
    active: bool
    category: ProductCategoryResponse
    addons: list[ProductAddonResponse] = Field(default_factory=list)
    variant_groups: list[ProductVariantGroupResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
