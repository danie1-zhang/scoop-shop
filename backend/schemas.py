from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from typing import Optional


class FlavorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: Decimal
    available: bool
    created_at: datetime


class FlavorListResponse(BaseModel):
    items: list[FlavorResponse]
    page: int
    page_size: int
    total: int


class FlavorCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    available: bool = True


class FlavorUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    price: Optional[Decimal] = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    available: Optional[bool] = None

    @field_validator("name", "description", "price", "available")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("Field cannot be null")
        return value


class EmailCredentials(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserCreate(EmailCredentials):
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    created_at: datetime


class LoginRequest(EmailCredentials):
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CartItemRequest(BaseModel):
    flavor_id: int
    quantity: int = Field(..., ge=1, le=100)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, le=100)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    flavor_id: int
    quantity: int
    created_at: datetime
    flavor: FlavorResponse


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    flavor_id: int
    quantity: int
    price_at_purchase: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_price: Decimal
    created_at: datetime    
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    page: int
    page_size: int
    total: int
