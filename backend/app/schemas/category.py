from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Category name must contain at least two characters.")
        return normalized


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Category name must contain at least two characters.")
        return normalized

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one category field must be provided.")
        return self


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    active: bool
    created_at: datetime
    updated_at: datetime
